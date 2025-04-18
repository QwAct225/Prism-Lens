import os
import sys
import logging
import traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.data.preprocessing import JSONPreprocessor

# Setup logging
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
        OUTPUT_PATH = OUTPUT_DIR / 'arxiv_papers_processed.json'
        
        if not INPUT_PATH.exists():
            raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")
            
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
        processor = JSONPreprocessor()
        
        logging.info("Starting preprocessing...")
        logging.info(f"Input: {INPUT_PATH}")
        logging.info(f"Output: {OUTPUT_PATH}")
        
        processor.process_to_json(
            input_csv=str(INPUT_PATH),
            output_json=str(OUTPUT_PATH)
        )
        
        logging.info("Preprocessing completed successfully")
        logging.info(f"Output file size: {OUTPUT_PATH.stat().st_size} bytes")
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()