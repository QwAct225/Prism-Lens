import asyncio
import csv
from src.data import ArXivScraper, TextCleaner

async def main():
    # Initialize components
    scraper = ArXivScraper()
    cleaner = TextCleaner()
    
    # Run scraping pipeline
    print("Memulai proses scraping...")
    raw_titles = await scraper.crawl_all()
    
    # Clean data
    print("\nMembersihkan data...")
    cleaned_titles = cleaner.clean_batch(raw_titles)
    
    # Save to CSV
    with open('arxiv_titles_raw.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Number', 'Title'])
        writer.writerows(enumerate(cleaned_titles, 1))
    
    print(f"\nBerhasil menyimpan {len(cleaned_titles)} judul ke arxiv_titles_raw.csv")

if __name__ == "__main__":
    asyncio.run(main())