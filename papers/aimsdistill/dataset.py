from torch.utils.data import DataLoader, Dataset
import torch
import numpy as np

# Example dataset class
class MyDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length, labels, teacher_logits=None):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.teacher_logits = teacher_logits
        if isinstance(self.teacher_logits, np.ndarray):    
            self.teacher_logits = torch.from_numpy(self.teacher_logits)
            print(" #####  ", isinstance(self.teacher_logits, np.ndarray))
 
    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        # Tokenize the text and return input_ids and attention_mask
        inputs = self.tokenizer(text, return_tensors="pt", padding='max_length', truncation=True, max_length=self.max_length)
        input_ids = inputs['input_ids'].squeeze(0)  # Remove the batch dimension
        attention_mask = inputs['attention_mask'].squeeze(0)
        labels = torch.tensor(self.labels[idx], dtype=torch.float32)
        if self.teacher_logits is None:
            return (input_ids, attention_mask), labels, False
        else:
            teacher_logits = self.teacher_logits[idx]
            return (input_ids, attention_mask), labels, teacher_logits
