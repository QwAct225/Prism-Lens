import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.preprocessing import TextCleaner

input_file = "arxiv_papers_raw.csv"
output_file = "arxiv_papers_cleaned.csv"

print("Loading data...")
df = pd.read_csv(input_file)

cleaner = TextCleaner()

print("Cleaning data...")
cleaned_df = cleaner.clean_batch(df)

final_df = cleaned_df[[
    'ID',
    'cleaned_title', 
    'cleaned_authors', 
    'cleaned_abstract'
]].rename(columns={
    'cleaned_title': 'Title',
    'cleaned_authors': 'Authors',
    'cleaned_abstract': 'Abstract'
})

final_df.to_csv(output_file, index=False)
print(f"Preprocessing complete! Cleaned file saved as: {output_file}")