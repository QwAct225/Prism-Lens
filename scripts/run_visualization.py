import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils.plot_utils import plot_top_authors, plot_authors_per_paper, plot_author_wordcloud
from src.utils.plot_utils import plot_word_frequency, plot_word_cloud, plot_title_length_distribution

df = pd.read_csv("../data/arxiv_papers_cleaned.csv")

plot_word_frequency(df["cleaned_title"])
plot_word_cloud(df["cleaned_title"])
plot_title_length_distribution(df)

plot_top_authors(df, top_n=15)
plot_authors_per_paper(df)
plot_author_wordcloud(df)