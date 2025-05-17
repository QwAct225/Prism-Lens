import asyncio
import csv
from datetime import datetime
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.data.scraper import ArXivScraper


async def main():
    scraper = ArXivScraper()
    papers = await scraper.crawl_papers()

    paper_with_id = []
    for idx, paper_dict in enumerate(papers, 1):
        paper_dict["ID"] = idx
        paper_with_id.append(paper_dict)

    output_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'arxiv_papers_raw.csv')

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ID",
            "Title",
            "Authors",
            "Abstract",
            "Journal_Conference_Name",
            "Publisher",
            "Year",
            "DOI",
            "Group_Name"
        ])
        writer.writeheader()
        writer.writerows(paper_with_id)

    print(f"Data tersimpan di {output_path} dengan {len(papers)} paper")

    # Tambahkan output untuk API
    print(f"RESULTS_FILE:{output_path}")


if __name__ == "__main__":
    asyncio.run(main())