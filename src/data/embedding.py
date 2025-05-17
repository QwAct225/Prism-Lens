from transformers import BertTokenizer, BertModel
import torch
import pandas as pd
import numpy as np

class BERTEmbedder:
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()  # Set model to evaluation mode

    def embed_text(self, text):
        """Generate BERT embeddings for a given text input."""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().numpy()  # CLS token embedding

    def embed_titles(self, df, text_column="title"):
        """Embed all titles in the dataframe and return numpy array."""
        embeddings = np.array([self.embed_text(title) for title in df[text_column]])
        return embeddings