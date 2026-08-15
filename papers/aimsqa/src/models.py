"""Model definition used by the fine-grained context classifier."""

import torch
from torch import nn
from transformers import AutoModel


class ContextClassifier(nn.Module):
    """ModernBERT encoder with an 11-label classification head."""

    def __init__(self, model_path: str, dropout: float = 0.4) -> None:
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.encoder.config.hidden_size, 11)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        output = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = output.last_hidden_state[:, 0, :]
        return self.dropout(self.classifier(pooled))
