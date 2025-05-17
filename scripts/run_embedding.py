import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.embedding import BERTEmbedder


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(base_dir, "data", "processed", "arxiv_papers_cleaned.csv")
    output_path = os.path.join(base_dir, "data", "embeddings.npy")

    if not os.path.exists(input_path):
        print(f"Error: File input tidak ditemukan di {input_path}")
        return

    print(f"Membaca data dari {input_path}")
    df = pd.read_csv(input_path)

    if "title" not in df.columns:
        print("Error: Kolom 'Title' tidak ditemukan dalam data")
        return

    print(f"Membuat embeddings untuk {len(df)} paper...")
    embedder = BERTEmbedder()
    title_embeddings = embedder.embed_titles(df, text_column="title")

    print(f"Menyimpan embeddings ke {output_path}")
    np.save(output_path, title_embeddings)

    print(f"Saved {title_embeddings.shape} embeddings to {output_path}")


if __name__ == "__main__":
    main()