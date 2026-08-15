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
from functions import *

LANGUAGE_MODEL = "gemma3:27b"
device = "cuda"
model_name = "./modernbert-mlm-ca10"
tokenizer = AutoTokenizer.from_pretrained(model_name,trust_remote_code=True)
model = SentenceBERTForDownstreamTask(tokenizer, model_name,dropout=0.4)
model.load_state_dict(torch.load("au_20250401-084410.pth", map_location=torch.device('cpu')))
model.to(device)
model.eval()

model_sb = SentenceTransformer("../ft-sb/output_retriever_win5").to(device)

input_query = [
    "approval",
    "signature",
    "c1 (reporting entity)",
    "c2 (structure)",
    "c2 (operations)",
    "c2 (supply chains)",
    "c3 (risk description)",
    "c4 (risk mitigation)",
    "c4 (remediation)",
    "c5 (effectiveness)",
    "c6 (consultation)"
]


df0 = pd.read_csv("../AU.csv")
sim_dictionary = {}
criterion_list=[]
question_list = []
keyword_list = []
response_list = []
answer_list = []
context_list = []
id_list = []
sentence_list = []
ids = set(df0['statement_id'].tolist())
df0 = create_context(df0)
max_retries = 5
for this_id in ids:
#for this_id in [11135]:
    print("this id ",this_id)
    df = df0[df0['statement_id'] == this_id]
    dataset = df.sentence.tolist()
    context = df.context.tolist()
    label = df.targets.apply(lambda x: ast.literal_eval(x)).tolist()

    idx = 0
    positive_contexts, positive_sentences= obtain_sentences_clf(dataset, context, input_query, tokenizer, model, threshold = 0.7)
    all_questions = pd.read_csv("questions.csv", encoding='ISO-8859-1')
    
    for index, row in all_questions.iterrows():
      if pd.isna(row["Questions"]) or pd.isna(row["Criterion"]) or len(row["Questions"]) == 0:  
        continue
      
      criterion_list.append(row["Criterion"])
      print("Current question ", row["Questions"])
      question_list.append(row["Questions"])
      keyword_list.append(row["Keywords"])
      idx +=1
      print("Criterion ",row["Criterion"])
      new_context = criterion_mapping(input_query, row["Criterion"], positive_contexts)
      new_sentences = criterion_mapping(input_query, row["Criterion"], positive_sentences)  
      sentences_str = '\n'.join([f' - {chunk}' for chunk in new_sentences])
      sentence_list.append(sentences_str)
      if len(new_context) != 0:
           print("new_context: ",new_context) 
           print("clf based generation,,,,,,,,")
           context_str = '\n'.join([f' - {chunk}' for chunk in new_context])
           prompt_clf = f"""You are a helpful chatbot. Use only the following pieces of context to answer the question. Don't make up any new information. Answer with ###Answer### + "Yes" or "No": {context_str}"""

           answer, this_chunk = run_retry(row["Questions"], prompt_clf ,max_retries,LANGUAGE_MODEL)
           print("#######clf response ", this_chunk)
           if answer != -1:
              cell_value = "\n".join([f"{item}" for i, item in enumerate(new_context)])
              context_list.append(cell_value)

      
      if len(new_context) == 0 or answer == -1:
             print("retriving,,,,,,,,,")
             chunks = chunk_statement(dataset, chunk_size=5, stride=2, min_final_chunk=1)
             current_contexts = obtain_sentences_sb(chunks, row["Questions"], model_sb)
             print("current_contexts ",current_contexts)
             context_str = '\n'.join([f' - {chunk}' for chunk in current_contexts])
             prompt_sb = f"""You are a helpful chatbot. Use only the following pieces of context to answer the question. Don't make up any new information. Answering with ###Answer### + "Yes" or "No":{context_str}"""
             print("###########prompt_sb ",prompt_sb)
             answer, this_chunk = run_retry(row["Questions"], prompt_sb ,max_retries,LANGUAGE_MODEL)
             print("@@@retrieve response: ",this_chunk)
             cell_value = "\n".join([f"{item}" for i, item in enumerate(current_contexts)])
             context_list.append(cell_value)

      answer_list.append(answer)
      response_list.append(this_chunk)

    df = pd.DataFrame({
    "Criterion": criterion_list,
    "Keywords": keyword_list,
    "Question":question_list,
    "Answer": answer_list,
    "Context": context_list,
    "Sentences": sentence_list,
    "LLM_response": response_list
    })

    df.to_csv("./results/output_"+str(this_id)+".csv")

#timestamp_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#with open('similarity_'+timestamp_str+'.pkl', 'wb') as f:
#    pickle.dump(sim_dictionary, f)
#
#with open('response_'+timestamp_str+'.pkl', 'wb') as f:
#    pickle.dump(response, f)
#
#with open('prediction_'+timestamp_str+'.pkl', 'wb') as f:
#    pickle.dump(predicted, f)

