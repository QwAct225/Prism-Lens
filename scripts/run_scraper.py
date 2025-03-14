import asyncio
import csv
from src.data import ArXivScraper

async def main():
    # Initialize scraper
    scraper = ArXivScraper()
    
    # Run scraping pipeline
    print("Memulai proses scraping...")
    papers = await scraper.crawl_all()
    
    # Save to CSV
    with open('arxiv_papers_raw.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Authors'])
        for title, authors in papers:
            writer.writerow([title, authors])
    
    print(f"\nBerhasil menyimpan {len(papers)} paper ke arxiv_papers_raw.csv")

if __name__ == "__main__":
    asyncio.run(main())