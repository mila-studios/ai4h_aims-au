"""Check for the AIMS-QA model weights and explain where to get them.

The weights are too large to keep in the git repository (the classifier alone is
1.47 GB, and GitHub's free Git LFS allowance is 1 GB in total), so they are
archived on Figshare with DOIs. Run this after cloning to see what is missing.

The ModernBERT backbone (answerdotai/ModernBERT-large) is not listed here: it is
downloaded automatically by transformers on first use.
"""

from pathlib import Path

AIMSDISTILL_DOI = "https://doi.org/10.6084/m9.figshare.33261576"
AIMSQA_DOI = "https://doi.org/10.6084/m9.figshare.33261639"

REQUIRED = [
    (
        Path("models/context_classifier.pth"),
        "1.47 GB",
        f"Download 'au.pth' from {AIMSDISTILL_DOI}\n"
        "     and save it as models/context_classifier.pth",
    ),
    (
        Path("models/sentencebert_retriever/model.safetensors"),
        "87 MB",
        f"Download 'sentencebert_retriever.zip' from {AIMSQA_DOI}\n"
        "     and unzip it into models/sentencebert_retriever/",
    ),
]


def main() -> None:
    missing = [(p, size, how) for p, size, how in REQUIRED if not p.exists()]

    if not missing:
        print("All model weights present. You can run pipeline.py.")
        return

    print(f"{len(missing)} of {len(REQUIRED)} model file(s) missing:\n")
    for path, size, how in missing:
        print(f"  {path}  ({size})")
        print(f"     {how}\n")
    print("Agent 1 needs the classifier. Agent 2 (the RAG Watchdog fallback) needs")
    print("the retriever; without it, questions Agent 1 cannot answer are skipped.")


if __name__ == "__main__":
    main()

