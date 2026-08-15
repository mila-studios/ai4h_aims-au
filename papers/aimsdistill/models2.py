import torch
from torch import nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
class AimsDistillModel(nn.Module):
    def __init__(self,tokenizer, model_name,dropout):
        super(AimsDistillModel, self).__init__() 
        model = AutoModel.from_pretrained(model_name,trust_remote_code=True)
        for param in model.parameters():
            param.requires_grad = True
        self.m = nn.Dropout(p=dropout)
        self.bert = model
        embedding_dim = model.config.hidden_size

        self.classifier = nn.Linear(model.config.hidden_size, 11)  # 2 for binary classification

    def forward(self, input_ids, attention_mask=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0, :]
        logits = self.m(self.classifier(pooled_output))
        return logits

