import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List

def download_nltk_resources():
    """Download necessary NLTK resources (only once)."""
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

class TextCleaner:
    def __init__(self):
        download_nltk_resources()  
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.regex = re.compile(r'[^a-zA-Z\s-]')  

    def clean_title(self, title: str) -> str:
        """Text normalization pipeline"""
        cleaned = self.regex.sub('', title).lower()
        
        tokens = cleaned.split()
        filtered = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]
        
        return ' '.join(filtered)
    
    def clean_authors(self, authors: str) -> str:
        """Cleans author names while preserving first and last names"""
        if pd.isna(authors):  
            return ""

        cleaned = self.regex.sub('', authors)
        cleaned = ' '.join(cleaned.split()) 
        return cleaned  

    def clean_batch(self, titles: List[str]) -> List[str]:
        """Batch processing"""
        return [self.clean_title(title) for title in titles]