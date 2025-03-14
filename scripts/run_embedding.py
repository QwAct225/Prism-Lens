import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.embedding import BERTEmbedder

df = pd.read_csv("../data/arxiv_papers_cleaned.csv") 

embedder = BERTEmbedder()

title_embeddings = embedder.embed_titles(df, text_column="Title")

np.save("../data/embeddings.npy", title_embeddings)

print(f"Saved {title_embeddings.shape} embeddings to data/embeddings.npy")