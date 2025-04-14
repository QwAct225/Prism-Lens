import asyncio
import csv
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.data.scraper import ArXivScraper

async def main():
    scraper = ArXivScraper()

    print("Memulai proses scraping...")
    papers = await scraper.crawl_all()

    with open('arxiv_papers_raw.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Authors', 'Abstract'])
        for idx, (title, authors, abstract) in enumerate(papers, 1):
            writer.writerow([idx, title, authors, abstract])
    
    print(f"\nBerhasil menyimpan {len(papers)} paper ke arxiv_papers_raw.csv")

if __name__ == "__main__":
    asyncio.run(main())