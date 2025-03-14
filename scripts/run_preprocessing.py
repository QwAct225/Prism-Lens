import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.preprocessing import TextCleaner

# Load dataset
input_file = "../data/arxiv_papers_raw.csv"
output_file = "../data/arxiv_papers_cleaned.csv"

print("Loading data...")
df = pd.read_csv(input_file)

# Initialize text cleaner
cleaner = TextCleaner()

print("Cleaning text...")
df["cleaned_title"] = df["Title"].apply(cleaner.clean_title)
df["cleaned_authors"] = df["Authors"].apply(cleaner.clean_authors)

# Save cleaned data
df.to_csv(output_file, index=False)
print(f"Preprocessing complete! Cleaned file saved as: {output_file}")