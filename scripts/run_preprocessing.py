import os
import sys
import logging
import traceback
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.data.preprocessing import JSONPreprocessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preprocessing.log'),
        logging.StreamHandler()
    ]
)


def main():
    try:
        BASE_DIR = Path(__file__).parent.parent
        INPUT_PATH = BASE_DIR / 'data/raw/arxiv_papers_raw.csv'
        OUTPUT_DIR = BASE_DIR / 'data/processed'
        OUTPUT_JSON_PATH = OUTPUT_DIR / 'arxiv_papers_processed.json'
        OUTPUT_CSV_PATH = OUTPUT_DIR / 'arxiv_papers_cleaned.csv'

        if not INPUT_PATH.exists():
            raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        processor = JSONPreprocessor()

        logging.info("Starting preprocessing...")
        logging.info(f"Input: {INPUT_PATH}")
        logging.info(f"Output JSON: {OUTPUT_JSON_PATH}")
        logging.info(f"Output CSV: {OUTPUT_CSV_PATH}")

        # Proses ke JSON
        processor.process_to_json(
            input_csv=str(INPUT_PATH),
            output_json=str(OUTPUT_JSON_PATH)
        )

        df = pd.read_csv(INPUT_PATH)
        df_cleaned = df.copy()

        if 'Title' in df_cleaned.columns:
            df_cleaned['Title'] = df_cleaned['Title'].str.strip()
            df_cleaned['Title'] = df_cleaned['Title'].str.replace(r'\s+', ' ', regex=True)

        if 'Authors' in df_cleaned.columns:
            df_cleaned['Authors'] = df_cleaned['Authors'].str.strip()

        df_cleaned.to_csv(OUTPUT_CSV_PATH, index=False)

        logging.info("Preprocessing completed successfully")
        logging.info(f"JSON output file size: {OUTPUT_JSON_PATH.stat().st_size} bytes")
        logging.info(f"CSV output file size: {OUTPUT_CSV_PATH.stat().st_size} bytes")

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()