import torch
from torch import nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
class SentenceBERTForDownstreamTask(nn.Module):
    def __init__(self,tokenizer, model_name,dropout):
        super(SentenceBERTForDownstreamTask, self).__init__() 
        model_SB = AutoModel.from_pretrained(model_name,trust_remote_code=True)
        for param in model_SB.parameters():
            param.requires_grad = True
        self.m = nn.Dropout(p=dropout)
        self.bert = model_SB
        embedding_dim = model_SB.config.hidden_size

        self.classifier = nn.Linear(model_SB.config.hidden_size, 11)  # 2 for binary classification

    def forward(self, input_ids, attention_mask=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0, :]
        logits = self.m(self.classifier(pooled_output))
        return logits, pooled_output

class DistillationModel(nn.Module):
    def __init__(self):
        super(DistillationModel, self).__init__()

        # Initialize 5 weights for the 5 logits
        init_weights = torch.tensor([0.4, 0.4, 0.05, 0.05, 0.1])
        self.logit_weights = nn.Parameter(init_weights.log()) 

    def forward(self, args):
        # Load all logits
        logits_list = [
            load_tensor("../logits/train_prompt_logits.pt"),
            load_tensor("../logits/train_" + args.dataset + "_logits.pt"),
            load_tensor("../logits/cl_5_6.pt"),
            load_tensor("../logits/cl_7_8.pt"),
            load_tensor("../logits/cl_7_9.pt"),
        ]

        # Apply softmax to ensure weights sum to 1
        weights = F.softmax(self.logit_weights, dim=0)

        # Weighted sum of teacher logits
        teacher_logits = sum(w * l for w, l in zip(weights, logits_list))

        return teacher_logits
