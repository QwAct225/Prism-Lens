import os
import sys
import logging
import traceback
from pathlib import Path

import pandas as pd

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
        logging.info(f"Input CSV: {INPUT_PATH}")
        logging.info(f"Output JSON: {OUTPUT_JSON_PATH}")
        logging.info(f"Output CSV: {OUTPUT_CSV_PATH}")

        # Run full preprocessing to JSON
        processor.process_to_json(
            input_csv=str(INPUT_PATH),
            output_json=str(OUTPUT_JSON_PATH)
        )

        # Optional: Load JSON and write cleaned CSV version (flattened)
        with open(OUTPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            cleaned_data = pd.read_json(f)

        cleaned_data.to_csv(OUTPUT_CSV_PATH, index=False)

        logging.info("Preprocessing completed successfully")
        logging.info(f"JSON output size: {OUTPUT_JSON_PATH.stat().st_size} bytes")
        logging.info(f"CSV output size: {OUTPUT_CSV_PATH.stat().st_size} bytes")

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
