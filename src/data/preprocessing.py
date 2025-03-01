import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List

nltk.download('stopwords')
nltk.download('wordnet')

class TextCleaner:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.regex = re.compile(r'[^a-zA-Z0-9\s-]')

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

    def clean_batch(self, titles: List[str]) -> List[str]:
        """Batch processing"""
        return [self.clean_title(title) for title in titles]