import json
import pandas as pd
import numpy as np
import re
from typing import Dict, Any

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')


class JSONPreprocessor:
    def __init__(self):
        self.required_columns = [
            'ID', 'Title', 'Authors', 'Abstract',
            'Journal_Conference_Name', 'Publisher',
            'Year', 'DOI', 'Group_Name'
        ]
        self.stop_words = set(stopwords.words('english'))

    def _validate_row(self, row: Dict) -> bool:
        return all(col in row for col in self.required_columns)

    def _clean_authors(self, authors_str: str) -> list:
        if pd.isna(authors_str) or authors_str.strip() == '':
            return []
        return [author.strip() for author in authors_str.split(';')]

    def _clean_year(self, year) -> int:
        try:
            return int(float(year)) if not pd.isna(year) else None
        except:
            return None

    def preprocess_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        tokens = word_tokenize(text)
        tokens = [
            t for t in tokens if t not in self.stop_words and len(t) > 2
        ]
        return ' '.join(tokens)

    def clean_entry(self, row: Dict) -> Dict[str, Any]:
        try:
            raw_title = str(row.get('Title', '')).strip()
            cleaned_title = self.preprocess_text(raw_title)

            return {
                "id": str(row.get('ID', '')).strip(),
                "title": cleaned_title,
                "abstract": str(row.get('Abstract', '')).strip(),
                "authors": self._clean_authors(row.get('Authors', '')),
                "journal_conference_name": str(row.get('Journal_Conference_Name', '')).strip(),
                "publisher": str(row.get('Publisher', '')).strip(),
                "year": self._clean_year(row.get('Year')),
                "doi": str(row.get('DOI', '')).strip(),
                "group_name": str(row.get('Group_Name', '')).strip()
            }
        except Exception as e:
            print(f"Error processing row: {e}")
            return None

    def process_to_json(self, input_csv: str, output_json: str):
        try:
            df = pd.read_csv(input_csv, keep_default_na=False)

            missing_cols = [col for col in self.required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            processed_data = []
            for _, row in df.iterrows():
                if self._validate_row(row):
                    cleaned = self.clean_entry(row)
                    if cleaned:
                        processed_data.append(cleaned)

            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(
                    processed_data,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=lambda x: str(x) if isinstance(x, (np.int64, np.float64)) else x
                )

            print(f"Successfully processed {len(processed_data)}/{len(df)} entries")

        except Exception as e:
            print(f"Processing failed: {str(e)}")
            raise