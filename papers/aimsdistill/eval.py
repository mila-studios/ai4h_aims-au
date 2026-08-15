import torch
from torch.utils.data import random_split, DataLoader
from tqdm import tqdm
import pickle
import random
import numpy as np
import torchmetrics
from torchmetrics.classification import Accuracy, F1Score
import argparse
from torch import nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from dataset import *
from models2 import *
from sklearn.metrics import f1_score
import pandas as pd
import time
import gc
import ast
import time


def train_batch(batch, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_ids, attention_mask = [b.to(device) for b in batch]  # Move to GPU
    logits = model(input_ids=input_ids, attention_mask=attention_mask)
    return logits

def evaluate(model, data_loader, loss_fn, batch_size, length):
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    total_loss = 0
    all_labels = []
    all_predictions = []

    # Original label names
    list_name = [
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

    # Merged label names
    merged_list_name = [
        "approval",
        "signature",
        "c1 (reporting entity)",
        "c2",  # merged from 3
        "c3 (risk description)",
        "c4",  # merged from 2
        "c5 (effectiveness)",
        "c6 (consultation)"
    ]

    c2_indices = [list_name.index(x) for x in list_name if x.startswith("c2 (")]
    c4_indices = [list_name.index(x) for x in list_name if x.startswith("c4 (")]

    def merge_columns(arr, c2_idx, c4_idx):
        c2_merged = np.max(arr[:, c2_idx], axis=1, keepdims=True)
        c4_merged = np.max(arr[:, c4_idx], axis=1, keepdims=True)
        keep_indices = [i for i in range(arr.shape[1]) if i not in c2_idx + c4_idx]
        kept = arr[:, keep_indices]
        return np.concatenate([kept[:, :3], c2_merged, kept[:, 3:4], c4_merged, kept[:, 4:]], axis=1)

    with torch.no_grad():
        for batch, labels, _ in tqdm(data_loader):
            logits = train_batch(batch, model)
            loss = loss_fn(logits.cpu(), labels.cpu()).mean()
            total_loss += loss.item() * batch_size

            predictions = (logits > 0.5).float()
            all_labels.extend(labels.cpu().numpy())
            all_predictions.extend(predictions.cpu().numpy())

    all_labels = np.array(all_labels)
    all_predictions = np.array(all_predictions)

    # Merge c2 and c4 labels
    all_labels_merged = merge_columns(all_labels, c2_indices, c4_indices)
    all_predictions_merged = merge_columns(all_predictions, c2_indices, c4_indices)

    # Calculate metrics
    avg_loss = total_loss / length
    micro_f1 = f1_score(all_labels_merged, all_predictions_merged, average='micro', zero_division=0)
    macro_f1 = f1_score(all_labels_merged, all_predictions_merged, average='macro', zero_division=0)
    weighted_f1 = f1_score(all_labels_merged, all_predictions_merged, average='weighted', zero_division=0)

    print("\nPer-label F1 Scores:")
    for i, name in enumerate(merged_list_name):
        f1 = f1_score(all_labels_merged[:, i], all_predictions_merged[:, i], zero_division=0)
        print(f"{name}: {f1:.3f}")

    print(f"\nAverage Loss: {avg_loss:.4f}")
    print(f"Micro-F1: {micro_f1:.3f}")
    print(f"Macro-F1: {macro_f1:.3f}")
    print(f"Weighted-F1: {weighted_f1:.3f}")

    return avg_loss, micro_f1, macro_f1, weighted_f1

    

def main(args):
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  epochs = args.epochs
  lr = args.lr
  bce_loss = nn.BCEWithLogitsLoss(reduction="none")
  batch_size = args.batch_size
  max_length = 60

  random_seed = 4335
  torch.manual_seed(random_seed)
  random.seed(random_seed)
  np.random.seed(random_seed)
  
  #model_name = "answerdotai/ModernBERT-large"
  #Load modernbert model. Use downloaded version since i was using HPC. can also use "answerdotai/ModernBERT-large" from huggingface
  model_name = "./modernbert-mlm"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  
  def load_tensor(path):
    obj = torch.load(path, map_location=torch.device("cpu"))
    if isinstance(obj, np.ndarray):
        return torch.tensor(obj, dtype=torch.float32)
    elif isinstance(obj, torch.Tensor):
        return obj.to(torch.float32)
    else:
        raise TypeError(f"Unsupported type: {type(obj)} in {path}")


  # weights = [0.45333151, 0.07288837, 0.13368368, 0.05638295, 0.14239221, 0.14132129]

  df = pd.read_csv('test.csv')
  labels = df.iloc[:,-11:].apply(lambda row: row.tolist(), axis=1).tolist()
  texts = df.sentence.tolist()
  test_dataset = MyDataset(texts, tokenizer, max_length, labels)


  test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

  start_time = time.time()
  # If you are training, here’s a basic training loop structure
  model = AimsDistillModel(tokenizer, model_name,dropout=args.dropout).to(device)
  state_dict = torch.load("AIMSDistill.pth", map_location=device)
  model.load_state_dict(state_dict)
  optimizer = torch.optim.Adam(model.parameters(), lr=lr)
  model.train()  # Set the model to train mode
  train_loss = []
  val_loss = []
  test_loss = []


  evaluate(model, test_loader, bce_loss,batch_size,len(test_dataset))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyTorch Training Script with Arguments")

    parser.add_argument("--epochs", type=int, default=1, help="Number of epochs to train the model")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for DataLoader")
    parser.add_argument("--lr", type=float, default=1e-5, help="learning rate for the model")
    parser.add_argument("--dropout", type=float, default=0.3, help="dropout")
    parser.add_argument("--temp", type=float, default=4.0, help="temprature")
    parser.add_argument("--alpha", type=float, default=0.1, help="alpha")
    parser.add_argument("--dataset", type=str, default="au", help="dataset")
    args = parser.parse_args()
    print("HYPERPARAMETERS@@@@@@@@@ learning rate",args.lr, " batch size :",args.batch_size," number of epochs ", args.epochs, " temprature ",args.temp, " alpha ", args.alpha)
    print("######## YOU ARE WORKING ON DATASET ", args.dataset)
    main(args)
