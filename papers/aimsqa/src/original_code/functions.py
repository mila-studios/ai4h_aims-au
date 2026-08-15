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
from models2 import *
from sklearn.metrics import f1_score
import numpy as np
import re
import ollama
import pickle
from datetime import datetime
import pandas as pd
import pandas as pd
import ast
from sentence_transformers import SentenceTransformer, util

device = "mps"

def split_context(context_str, max_words=930):
    words = context_str.split(" ")
    chunks = []

    for i in range(0, len(words), max_words):
        chunk_words = words[i:i + max_words]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)

    return chunks


def predict(x, tokenizer, model):

    tv = torch.tensor([tokenizer.encode(v, padding="max_length", max_length=60, truncation=True) for v in x])
    tv = tv.to(device)
    attention_mask = (tv != 0).type(torch.int64)
    outputs = model(tv, attention_mask=attention_mask)
    embedding = outputs[0].detach().cpu().numpy()
    return embedding[0]

def chunk_statement(sentences, chunk_size, stride, min_final_chunk):

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


def create_context(df, window=2):
    # Ensure correct ordering
    df = df.sort_values(by=['statement_id', 'sentence_orig_idxs']).reset_index(drop=True)

    def add_context(group):
        sentences = group['sentence'].tolist()
        context_list = []
        for i in range(len(sentences)):
            start = max(0, i - window)
            end = i + window + 1
            context = ' '.join(sentences[start:i] + [sentences[i]] + sentences[i+1:end])
            context_list.append(context)
        group['context'] = context_list
        return group

    return df.groupby('statement_id', group_keys=False).apply(add_context)

def generator(query, instruction,LANGUAGE_MODEL):
    stream = ollama.chat(
                    model=LANGUAGE_MODEL,
                    messages=[
                        {'role': 'system', 'content': instruction},
                        {'role': 'user', 'content': query},
                    ],
                    stream=True,
                    options={
                        "temperature": 0.5  # Lower = more deterministic, higher = more diverse 0.2prev
                    }
                )

    this_chunk = ""
    for chunk in stream:
              this_chunk+=chunk['message']['content']
    return this_chunk

def obtain_sentences_clf( texts, contexts, input_query, tokenizer, model, threshold=0.63):
    positive_contexts = {key:[] for key in input_query}
    positive_sentences = {key:[] for key in input_query} 
    for t, c in zip(texts, contexts):
        similarity = predict([t], tokenizer, model)
        similarity = 1 / (1 + np.exp(-similarity))
        
        for s, criteria in zip(similarity, input_query):

            if s > threshold:
                positive_contexts[criteria].append(c)
                positive_sentences[criteria].append(t)
    return positive_contexts, positive_sentences

def criterion_mapping(input_query, criterion, keyword, contexts):
    available = []
    for i in input_query:
        if criterion.lower() in i:
           print("DEBUGING LINE ", criterion, "keyword ",keyword)
           if "c2" in criterion.lower() or "c4" in criterion.lower():
              print("YOUR KEY WORD IS ", keyword.split(" ")[0])
              if keyword.split(" ")[0] in i:
                available += contexts[i]

           else:
                available += contexts[i]
    return available

def reasoning_mapping(input_query, criterion,  keyword, contexts):
    available = ""
    for i in input_query:
        if criterion.lower() in i:
           print("DEBUGING LINE ", criterion, "keyword ",keyword)
           if "c2" in criterion.lower() or "c4" in criterion.lower():
              print("YOUR KEY WORD IS ", keyword.split(" ")[0])
              if keyword.split(" ")[0] in i:
                available += "\n"
                available += contexts[i]
               
           else:
                available += "\n"
                available += contexts[i]

    return available

#def obtain_sentences_clf(texts, contexts, input_query, tokenizer, model, threshold=0.7):
#        positive_contexts = {key: [] for key in list(input_query.keys())}
#        criteria3_candidates = []
#
#        for t, c in zip(texts, contexts):
#            similarity = predict([t], tokenizer, model)
#            similarity = 1 / (1 + np.exp(-similarity))  # Apply sigmoid to all label scores
#
#            for s, criteria in zip(similarity, list(input_query.keys())):
#                   if criteria == "c3 (risk description)":
#                        if s > threshold:
#                            criteria3_candidates.append((s, c))
#                   else:
#                        if s > threshold:
#                            positive_contexts[criteria].append(c)
#        if criteria3_candidates:
#           top3 = sorted(criteria3_candidates, key=lambda x: x[0], reverse=True)[:5]
#           positive_contexts["c3 (risk description)"].extend([c for _, c in top3])
#
#        return positive_contexts

def obtain_sentences_sb(chunks, question, model, top_k=3, batch_size=64):
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
    top_k_idxs = sorted(range(len(best_scores)), key=lambda i: best_scores[i], reverse=True)[:top_k]
    return [best_chunks[i] for i in top_k_idxs]

def run_retry(query, instruction_prompt ,max_retries,LANGUAGE_MODEL):

    for attempt in range(1, max_retries + 1):
            this_chunk = generator(query, instruction_prompt,LANGUAGE_MODEL)

            if "YES" in this_chunk and "NO" not in this_chunk:
                return 1, this_chunk
            elif "NO" in this_chunk and "YES" not in this_chunk:
                return 0, this_chunk
            else:
                print(f"[Retry {attempt}/{max_retries}] somehow no answer and this is the response: ", this_chunk)
    return -1, this_chunk

