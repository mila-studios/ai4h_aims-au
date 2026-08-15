"""Distilled context classification -> fallback retrieval -> LLM QA pipeline."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import ollama
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer

from models import ContextClassifier
from prompts import CRITERIA, LABELS, QA_PROMPT


ROOT = Path(__file__).resolve().parent


def choose_device(requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def add_context_windows(frame: pd.DataFrame, window: int = 2) -> pd.DataFrame:
    frame = frame.sort_values(["statement_id", "sentence_orig_idxs"]).copy()

    def add(group: pd.DataFrame) -> pd.DataFrame:
        sentences = group["sentence"].fillna("").astype(str).tolist()
        group = group.copy()
        group["context"] = [
            " ".join(sentences[max(0, i - window) : i + window + 1])
            for i in range(len(sentences))
        ]
        return group

    groups = [add(group) for _, group in frame.groupby("statement_id", sort=False)]
    return pd.concat(groups, ignore_index=True) if groups else frame.assign(context="")


def make_chunks(sentences: list[str], size: int = 5, stride: int = 2) -> list[str]:
    if not sentences:
        return []
    starts = list(range(0, max(1, len(sentences) - size + 1), stride))
    chunks = [" ".join(sentences[start : start + size]) for start in starts]
    final = " ".join(sentences[-size:])
    if final and final not in chunks:
        chunks.append(final)
    return chunks


class PaperPipeline:
    def __init__(self, device: str, threshold: float, llm: str, max_retries: int = 5) -> None:
        self.device = choose_device(device)
        self.threshold = threshold
        self.llm = llm
        self.max_retries = max_retries
        classifier_dir = ROOT / "models" / "modernbert"
        self.tokenizer = AutoTokenizer.from_pretrained(classifier_dir, trust_remote_code=True)
        self.classifier = ContextClassifier(str(classifier_dir))
        state = torch.load(ROOT / "models" / "context_classifier.pth", map_location="cpu", weights_only=True)
        # The training code named the encoder `bert`. Rename only that prefix:
        # a global replacement would also corrupt keys such as `norm.weight`.
        state = {
            (f"encoder.{key.removeprefix('bert.')}" if key.startswith("bert.") else key): value
            for key, value in state.items()
        }
        self.classifier.load_state_dict(state)
        self.classifier.to(self.device).eval()
        self.retriever = SentenceTransformer(str(ROOT / "models" / "sentencebert_retriever"), device=self.device)

    @torch.inference_mode()
    def classified_contexts(self, sentences: list[str], contexts: list[str]) -> dict[str, list[str]]:
        selected = {label: [] for label in LABELS}
        for sentence, context in zip(sentences, contexts):
            encoded = self.tokenizer(
                sentence, return_tensors="pt", padding=True, truncation=True, max_length=60
            ).to(self.device)
            scores = torch.sigmoid(self.classifier(**encoded))[0].cpu().tolist()
            for label, score in zip(LABELS, scores):
                if score > self.threshold:
                    selected[label].append(context)
        return selected

    def retrieve(self, sentences: list[str], question: str, top_k: int = 3) -> list[str]:
        chunks = make_chunks(sentences)
        if not chunks:
            return []
        query_embedding = self.retriever.encode(question, convert_to_tensor=True, normalize_embeddings=True)
        chunk_embeddings = self.retriever.encode(chunks, convert_to_tensor=True, normalize_embeddings=True)
        scores = util.cos_sim(query_embedding, chunk_embeddings)[0]
        indices = torch.topk(scores, k=min(top_k, len(chunks))).indices.tolist()
        return [chunks[index] for index in indices]

    def ask(self, question: str, label: str, contexts: list[str]) -> tuple[str, str]:
        prompt = QA_PROMPT.format(
            criterion=CRITERIA[label],
            context="\n".join(f"- {item}" for item in contexts),
            question=question,
        )
        response = ""
        for attempt in range(1, self.max_retries + 1):
            response = ollama.chat(
                model=self.llm,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.0},
            )["message"]["content"]
            match = re.search(r"FINAL ANSWER:\s*(YES|NO|NOT ENOUGH INFORMATION)", response, re.I)
            if match:
                return match.group(1).upper(), response
            print(f"  Could not parse answer (attempt {attempt}/{self.max_retries})", flush=True)
        return "PARSE_ERROR", response

    def run(self, statements: pd.DataFrame, questions: pd.DataFrame) -> pd.DataFrame:
        statements = add_context_windows(statements)
        rows = []
        total = statements["statement_id"].nunique() * len(questions)
        completed = 0
        for statement_id, group in statements.groupby("statement_id", sort=False):
            sentences = group["sentence"].fillna("").astype(str).tolist()
            classified = self.classified_contexts(sentences, group["context"].tolist())
            for item in questions.to_dict("records"):
                completed += 1
                label = item["label"]
                question = item["question"]
                contexts = classified[label]
                source = "classifier"
                if not contexts:
                    contexts = self.retrieve(sentences, question)
                    source = "sentencebert"
                print(
                    f"[{completed}/{total}] statement={statement_id} label={label} "
                    f"source={source}",
                    flush=True,
                )
                answer, response = self.ask(question, label, contexts)
                if answer == "PARSE_ERROR" and source == "classifier":
                    contexts = self.retrieve(sentences, question)
                    source = "sentencebert_after_parse_error"
                    print("  Falling back to SentenceBERT after classifier-QA parse failure", flush=True)
                    answer, response = self.ask(question, label, contexts)
                rows.append({
                    "statement_id": statement_id,
                    "label": label,
                    "question": question,
                    "context_source": source,
                    "context": "\n".join(contexts),
                    "answer": answer,
                    "llm_response": response,
                })
        return pd.DataFrame(rows)


def load_questions(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    if {"label", "question"}.issubset(raw.columns):
        return raw[["label", "question"]].dropna()
    # Compatibility with the paper's original questions.csv.
    criterion_map = {
        "approval": "approval", "signature": "signature", "c1": "c1 (reporting entity)",
        "c2": None, "c3": "c3 (risk description)", "c4": None,
        "c5": "c5 (effectiveness)", "c6": "c6 (consultation)",
    }
    rows = []
    for item in raw.to_dict("records"):
        criterion = str(item.get("Criterion", "")).lower()
        keyword = str(item.get("Keywords", "")).strip().lower()
        label = criterion_map.get(criterion)
        if criterion == "c2":
            if keyword.startswith("operations"):
                label = "c2 (operations)"
            elif keyword.startswith("supply chains"):
                label = "c2 (supply chains)"
            else:
                label = "c2 (structure)"
        elif criterion == "c4":
            label = "c4 (remediation)" if keyword.startswith("remediation") else "c4 (risk mitigation)"
        question = item.get("Questions")
        if label and isinstance(question, str) and question.strip():
            rows.append({"label": label, "question": question.strip()})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "AU.csv")
    parser.add_argument("--questions", type=Path, default=ROOT / "data" / "questions.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "answers.csv")
    parser.add_argument("--llm", default="gemma3:27b")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--statement-id", type=int, help="Run one statement for a quick test")
    parser.add_argument(
        "--max-questions", type=int, help="Limit questions for a quick end-to-end smoke test"
    )
    args = parser.parse_args()

    statements = pd.read_csv(args.input)
    if args.statement_id is not None:
        statements = statements[statements["statement_id"] == args.statement_id]
    questions = load_questions(args.questions)
    if args.max_questions is not None:
        if args.max_questions < 1:
            parser.error("--max-questions must be at least 1")
        questions = questions.head(args.max_questions)
    if statements.empty:
        parser.error("no statements matched the requested input and --statement-id")
    if questions.empty:
        parser.error("no valid questions were loaded")
    if args.max_retries < 1:
        parser.error("--max-retries must be at least 1")
    result = PaperPipeline(args.device, args.threshold, args.llm, args.max_retries).run(
        statements, questions
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Saved {len(result)} answers to {args.output}")


if __name__ == "__main__":
    main()
