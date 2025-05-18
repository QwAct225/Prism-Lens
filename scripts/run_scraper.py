import asyncio
import csv
import os
import sys
import argparse
from datetime import datetime
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.data.scraper import ArXivScraper

async def main():
    parser = argparse.ArgumentParser(description='Scrape ArXiv papers')
    parser.add_argument('--query', type=str, default="MIT", help='Search query')
    parser.add_argument('--max-results', type=int, default=0, 
                       help='Maximum number of results (0 or negative means all)')
    parser.add_argument('--categories', type=str, help='Comma-separated list of ArXiv categories')
    parser.add_argument('--date-from', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--date-to', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--job-id', type=str, help='Job ID for API tracking')
    parser.add_argument('--preprocess', action='store_true', help='Preprocess the results')
    parser.add_argument('--append', action='store_true', default=True, help='Append to existing file')
    
    args = parser.parse_args()
    
    categories = None
    if args.categories:
        categories = args.categories.split(',')
    
    scraper = ArXivScraper()
    
    max_results = args.max_results if args.max_results > 0 else None
    
    start_time = datetime.now()
    print(f"Starting scraping at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    papers = await scraper.crawl_papers(
        query=args.query,
        max_results=max_results,
        categories=categories,
        date_from=args.date_from,
        date_to=args.date_to
    )
    
    duration = datetime.now() - start_time
    print(f"Scraping completed in {duration.total_seconds()/60:.2f} minutes")
    
    output_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'arxiv_papers_raw.csv')
    
    fieldnames = [
        "ID",
        "Title",
        "Authors",
        "Abstract",
        "Journal_Conference_Name",
        "Publisher",
        "Year",
        "DOI",
        "Group_Name"
    ]
    
    next_id = 1
    existing_data = []
    
    if os.path.exists(output_path) and args.append:
        try:
            df_existing = pd.read_csv(output_path)
            
            existing_columns = set(df_existing.columns)
            for col in existing_columns:
                if col not in fieldnames:
                    print(f"Menghapus kolom tambahan: {col}")
                    df_existing = df_existing.drop(columns=[col])
            
            for col in fieldnames:
                if col not in df_existing.columns:
                    print(f"Menambahkan kolom yang hilang: {col}")
                    df_existing[col] = ""
            
            existing_data = df_existing[fieldnames].to_dict('records')
            
            if 'ID' in df_existing.columns and not df_existing.empty:
                next_id = df_existing['ID'].max() + 1
                
            print(f"Existing data: {len(existing_data)} records. Next ID: {next_id}")
        except Exception as e:
            print(f"Error reading existing file: {str(e)}")
            print("Will create new file.")
            existing_data = []
    
    processed_papers = []
    for paper_dict in papers:
        processed_paper = {field: "" for field in fieldnames}
        processed_paper["ID"] = next_id
        
        for field in fieldnames:
            if field in paper_dict and field != "ID":
                processed_paper[field] = paper_dict[field]
                
        processed_papers.append(processed_paper)
        next_id += 1
    
    all_papers = existing_data + processed_papers
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_papers)
    
    print(f"Data tersimpan di {output_path}")
    print(f"Total data: {len(all_papers)} paper (Baru: {len(papers)}, Lama: {len(existing_data)})")
    print(f"RESULTS_FILE:{output_path}")
    
    if args.preprocess:
        try:
            preprocess_script = os.path.join(project_root, 'scripts', 'run_preprocessing.py')
            print(f"Menjalankan preprocessing: {preprocess_script}")
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, preprocess_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print("Preprocessing selesai dengan sukses")
            else:
                print(f"Preprocessing gagal dengan kode error {process.returncode}")
                print(f"Error: {stderr.decode()}")
                
        except Exception as e:
            print(f"Error menjalankan preprocessing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())