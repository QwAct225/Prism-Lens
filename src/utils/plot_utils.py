import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
import pandas as pd
from wordcloud import WordCloud
import numpy as np
import os

def save_plot(fig, filename, save_dir="../data/plots"):
    """Save the given figure to the specified directory."""
    os.makedirs(save_dir, exist_ok=True)  
    filepath = os.path.join(save_dir, filename)
    fig.savefig(filepath, bbox_inches="tight", dpi=300)
    print(f"Plot saved to {filepath}") 

def plot_word_frequency(titles, top_n=20):
    """Plots top N most frequent words from titles and saves the plot."""
    all_words = " ".join(titles)
    word_tokens = word_tokenize(all_words)
    
    word_freq = Counter(word_tokens)
    common_words = word_freq.most_common(top_n)
    words, counts = zip(*common_words)

    colors = plt.cm.viridis(np.linspace(0, 1, len(words)))  

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(words, counts, color=colors)  
    ax.set_xticklabels(words, rotation=45)
    ax.set_xlabel("Words")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Top {top_n} Most Frequent Words in Titles")

    save_plot(fig, "word_frequency.png")
    plt.show()

def plot_word_cloud(titles):
    """Generates a word cloud from the titles and saves the plot."""
    all_words = " ".join(titles)
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_words)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")  

    save_plot(fig, "word_cloud.png")
    plt.show()

def plot_title_length_distribution(df):
    """Plots distribution of title lengths and saves the plot."""
    df["title_length"] = df["Title"].apply(lambda x: len(x.split()))
    title_lengths = df["title_length"].value_counts().sort_index()
    colors = plt.cm.viridis(np.linspace(0, 1, len(title_lengths)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(title_lengths.index, title_lengths.values, color=colors, alpha=0.7)
    ax.set_xlabel("Number of Words in Title")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Title Lengths")
    ax.set_xticks(title_lengths.index)

    save_plot(fig, "title_length_distribution.png")
    plt.show()
    
def plot_top_authors(df, top_n=20):
    """Plot the top N most frequent authors and saves the plot."""
    all_authors = ", ".join(df["Authors"]).split(", ")  
    author_counts = Counter(all_authors)
    common_authors = author_counts.most_common(top_n)

    authors, counts = zip(*common_authors)

    colors = plt.cm.viridis(np.linspace(0, 1, len(authors)))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(authors, counts, color=colors)  
    ax.set_xticklabels(authors, rotation=45, ha='right')
    ax.set_xlabel("Authors")
    ax.set_ylabel("Number of Papers")
    ax.set_title(f"Top {top_n} Most Frequent Authors")

    save_plot(fig, "top_authors.png")
    plt.show()

def plot_authors_per_paper(df):
    """Plot histogram showing the number of authors per paper and saves the plot."""
    df["num_authors"] = df["Authors"].apply(lambda x: len(x.split(", ")))
    
    num_authors_counts = df["num_authors"].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.viridis(np.linspace(0, 1, len(num_authors_counts)))
    ax.bar(num_authors_counts.index, num_authors_counts.values, color=colors, alpha=0.8)
    ax.set_xlabel("Number of Authors per Paper")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Authors per Paper")
    ax.set_xticks(num_authors_counts.index)

    save_plot(fig, "authors_per_paper.png")
    plt.show()

def plot_author_wordcloud(df):
    """Generate a word cloud for author names and saves the plot."""
    all_authors = ", ".join(df["Authors"]).split(", ")
    author_counts = Counter(all_authors)
    wordcloud = WordCloud(width=1000, height=500, background_color="white", colormap="viridis",
                          normalize_plurals=False).generate_from_frequencies(author_counts)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud of Author Names")

    save_plot(fig, "author_word_cloud.png")
    plt.show()