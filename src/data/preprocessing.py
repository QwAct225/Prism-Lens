import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List

def download_nltk_resources():
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

class TextCleaner:
    def __init__(self):
        download_nltk_resources()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.title_regex = re.compile(r'[^a-zA-Z\s-]')
        self.abstract_regex = re.compile(r'[^a-zA-Z0-9\s\-.,;:!?]')

    def clean_title(self, title: str) -> str:
        cleaned = self.title_regex.sub('', title).lower()
        tokens = cleaned.split()
        filtered = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]
        return ' '.join(filtered)
    
    def clean_abstract(self, abstract: str) -> str:
        cleaned = self.abstract_regex.sub('', abstract)
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def clean_authors(self, authors: str) -> str:
        if pd.isna(authors):
            return ""
        return ' '.join(authors.split())

    def clean_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        df["cleaned_title"] = df["Title"].apply(self.clean_title)
        df["cleaned_authors"] = df["Authors"].apply(self.clean_authors)
        df["cleaned_abstract"] = df["Abstract"].apply(self.clean_abstract)
        return df