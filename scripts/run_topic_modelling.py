import pandas as pd
import os
import sys
import gc
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.topic_modelling import train_bertopic_model, print_top_keywords, reduce_topics, calculate_coherence_score, save_visualizations

def main():
    print("Starting topic modeling pipeline...")
    
    # Load data with sample limit
    print("Loading data...")
    df = pd.read_csv("../data/arxiv_papers_cleaned.csv")
    
    # Limit to a sample of documents (start with a smaller number to test)
    sample_size = 5000
    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)
        print(f"Sampled {sample_size} documents from dataset")
    
    titles = df["Title"].dropna().tolist()
    print(f"Processing {len(titles)} documents")
    
    # Train model with progress feedback
    print("Training BERTopic model...")
    model, topics = train_bertopic_model(titles)
    
    # Free up memory
    del df
    gc.collect()
    
    # Reduce the number of topics
    print("Reducing topics...")
    model = reduce_topics(model, titles, nr_topics=20)
    
    # Save the model
    print("Saving model...")
    save_path = "../data/bertopic_model"
    model.save(save_path)
    
    # Print top keywords of each topic
    print("\nTop keywords for each topic:")
    print_top_keywords(model)
    
    # Handle visualizations one by one with memory management
    print("\nGenerating visualizations (one at a time)...")
    save_visualizations(model, one_by_one=True)
    
    # Calculate coherence score with a smaller sample if needed
    print("\nCalculating coherence score...")
    coherence_sample = titles
    if len(titles) > 2000:  # Limit coherence calculation to 2000 docs if needed
        coherence_sample = titles[:2000]
        print(f"Using {len(coherence_sample)} documents for coherence calculation")
    
    tokenized_titles = [title.split() for title in coherence_sample]
    coherence = calculate_coherence_score(model, tokenized_titles)
    print(f"Coherence Score: {coherence}")
    
    print("Topic modeling completed successfully!")

if __name__ == "__main__":
    main()