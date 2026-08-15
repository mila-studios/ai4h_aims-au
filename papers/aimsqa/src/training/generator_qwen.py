import torch
from torch.utils.data import random_split, DataLoader
from tqdm import tqdm
import random
import torchmetrics
from torchmetrics.classification import Accuracy, F1Score
import argparse
from torch import nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics import f1_score
import numpy as np
import re
import ollama
import pickle
from datetime import datetime
import pandas as pd
import pandas as pd
import ast
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

device = "cuda"

model = SentenceTransformer("./output_retriever_win5").to(device)  # path to your fine-tuned model

LANGUAGE_MODEL = "qwen3:32b"

input_query = {
        "approval":"Was the company's Modern Slavery Act statement approved by the Board of Directors (or equivalent management body)?",
        "signature":"Was the company’s Modern Slavery Act statement signed by an appropriate person?",
        "c1 (reporting entity)":"",
        "c2 (structure)":"Does the company disclose its ownership structure?",
        "c2 (operations)":"Does the company disclose the operations?",
        "c2 (supply chains)":"Does the company identify suppliers in its supply chain or the regions where its supply chain is?",
        "c3 (risk description)":"Did the company identify any specific risks or incidents related to modern slavery?",
        "c4 (risk mitigation)":"Does the company outline specific actions or policies to address modern slavery in its supply chain?",
        "c4 (remediation)":"Did the company explain the corrective steps it has taken (or would take) in response to modern slavery incidents in their own operations and/or supply chain?",
        "c5 (effectiveness)":"Does the company define performance indicators that measure the effectiveness of their actions to combat slavery and trafficking?",
        "c6 (consultation)":"Does the statement mention consulting with any entities the company owns or controls?"
}

def obtain_sentences(chunks, question, model, top_k=3, batch_size=64):
    query_embedding = model.encode(question, convert_to_tensor=True, normalize_embeddings=True)
    best_scores = []
    best_chunks = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_embeddings = model.encode(batch, convert_to_tensor=True, normalize_embeddings=True)
        query_embedding = query_embedding.to(batch_embeddings.device)

        scores = util.cos_sim(query_embedding, batch_embeddings)[0]
        top_scores, top_idxs = torch.topk(scores, k=min(top_k, len(batch)))

        for score, idx in zip(top_scores, top_idxs):
            best_scores.append(score.item())
            best_chunks.append(batch[idx])

    # Keep only top_k across all batches
    top_k_idxs = sorted(range(len(best_scores)), key=lambda i: best_scores[i], reverse=True)[:top_k]
    return [best_chunks[i] for i in top_k_idxs]

df0 = pd.read_csv("../AU.csv")

sim_dictionary = {}
response = {}
predicted ={}
#this_id = 14094
ids = set(df0['statement_id'].tolist())

def chunk_statement(sentences: List[str], chunk_size: int = 5, stride: int = 1, min_final_chunk: int = 2) -> List[str]:
    """
    Splits a list of sentences into overlapping chunks.

    Parameters:
        sentences (List[str]): The list of sentence strings.
        chunk_size (int): Number of sentences per chunk.
        stride (int): Number of sentences to shift for next chunk (overlap = chunk_size - stride).
        min_final_chunk (int): Minimum number of remaining sentences to form a final partial chunk.

    Returns:
        List[str]: List of sentence chunks as concatenated strings.
    """
    chunks = []
    num_sentences = len(sentences)

    for i in range(0, num_sentences - chunk_size + 1, stride):
        chunk_text = " ".join(sentences[i:i + chunk_size])
        chunks.append(chunk_text)

    # Include the final partial chunk if needed
    last_start = num_sentences - chunk_size
    if num_sentences > 0 and (len(sentences) % stride != 0 or last_start + chunk_size > num_sentences):
        remaining = sentences[-min_final_chunk:]
        if len(remaining) >= min_final_chunk:
            final_chunk = " ".join(remaining)
            if final_chunk not in chunks:
                chunks.append(final_chunk)

    return chunks


# ids = (14402,0)
max_retries = 5
for this_id in ids:
#for this_id in [11135]:
    print("this id ",this_id)
    df = df0[df0['statement_id'] == this_id]
    dataset = df.sentence.tolist()
    label = df.targets.apply(lambda x: ast.literal_eval(x)).tolist()
    chunks = chunk_statement(dataset)

    this_result = []
    this_response = []
    this_sim = {}
    idx = 0

    for i in input_query:

        idx +=1
        current_contexts = obtain_sentences(dataset, i, model)
        this_sim[i] = current_contexts
        if i == "c1 (reporting entity)":
            this_result.append(-1)
            continue

        instruction_prompt = f'''You are a helpful chatbot.
        Use only the following pieces of context to answer the question. Don't make up any new information. Answering with ###Answer### + "Yes" or "No":
        {'\n'.join([f' - {chunk}' for chunk in current_contexts])}
        '''
        print("instruction_prompt ",instruction_prompt)
        for attempt in range(1, max_retries + 1):
            stream = ollama.chat(
                    model=LANGUAGE_MODEL,
                    messages=[
                        {'role': 'system', 'content': instruction_prompt},
                        {'role': 'user', 'content': input_query[i]},
                    ],
                    stream=True,
                    options={
                        "temperature": 0.7  # Lower = more deterministic, higher = more diverse
                    }
                )

            this_chunk = ""
            for chunk in stream:
              this_chunk+=chunk['message']['content']
            this_response.append(this_chunk)


            if "Yes" in this_chunk and "No" not in this_chunk:
                this_result.append(1)
                error = False
                break
            elif "No" in this_chunk and "Yes" not in this_chunk:
                this_result.append(0)
                error = False
                break
            else:
                print(f"[Retry {attempt}/{max_retries}] somehow no answer and this is the response: ", this_chunk)
                if attempt == max_retries:
                   this_result.append(-1)
    predicted[this_id]=this_result
    sim_dictionary[this_id] = this_sim
    response[this_id] = this_response

timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open('similarity_'+timestamp_str+'.pkl', 'wb') as f:
    pickle.dump(sim_dictionary, f)

with open('response_'+timestamp_str+'.pkl', 'wb') as f:
    pickle.dump(response, f)

with open('predicted_'+timestamp_str+'.pkl', 'wb') as f:
    pickle.dump(predicted, f)

def get_groundtruthe(label):
    ground_truth = [0 for i in range(11)]
    for this_label in label:
        for i, l in enumerate(this_label):
            if int(l) == 1:
                ground_truth[i]=1
    return ground_truth

import pandas as pd
import ast

df0 = pd.read_csv("../AU.csv")

groundtruth =[]
#this_id = 14094
ids = set(df0['statement_id'].tolist())
# ids = (14402,14618,14781)
for this_id in ids:
    df = df0[df0['statement_id'] == this_id]
    label = df.targets.apply(lambda x: ast.literal_eval(x)).tolist()
    groundtruth.append(get_groundtruthe(label))

import numpy as np
from sklearn.metrics import f1_score

# Assuming y_true and y_pred are both shape [n_samples, n_classes]
y_true = np.array(groundtruth)
y_pred = np.array(list(predicted.values()))
# y_pred = np.delete(y_pred, 3, axis=1)  # remove column 3 if needed
# y_pred = np.delete(y_pred, 2, axis=1)  # remove column 3 if needed
y_pred[y_pred == -1] = 0

# y_true = np.delete(y_true, 2, axis=1)

assert y_true.shape == y_pred.shape

num_classes = y_true.shape[1]
f1s = []

for i in range(num_classes):
    # Mask out -1 values for class i
    mask = y_true[:, i] != -1
    if np.any(mask):  # at least one valid label
        f1 = f1_score(y_true[mask, i], y_pred[mask, i], average='binary', zero_division=0)
    else:
        f1 = np.nan  # or 0 if you prefer
    f1s.append(f1)

f1s = np.array(f1s)

print("Per-label F1 scores:", f1s)
print("Macro F1 (mean over valid labels):", np.nanmean(f1s))

