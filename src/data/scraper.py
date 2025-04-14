import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple

class ArXivScraper:
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None

    async def crawl_page(self, start: int, size: int = 200) -> Optional[List[Tuple[str, str, str]]]:
        """Crawl individual arXiv page dan ekstrak title, authors, abstract"""
        url = f"https://arxiv.org/search/?query=MIT&searchtype=all&abstracts=show&order=-announced_date_first&size={size}&date-date_type=submitted_date&start={start}"
        html = await self.fetch_page(url)
        
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        results_message = soup.select_one('h1.title.is-clearfix')
        
        if results_message and "No results" in results_message.text:
            return []
            
        papers = []
        for result in soup.select('li.arxiv-result'):
            title = result.select_one('p.title.is-5.mathjax')
            if not title:
                continue
            clean_title = title.get_text(strip=True).replace("Title:", "")

            authors = result.select_one('p.authors')
            if not authors:
                clean_authors = "N/A"
            else:
                author_names = [
                    a.get_text(strip=True) 
                    for a in authors.select('a[href*="searchtype=author"]')
                ]
                clean_authors = ", ".join(author_names)

            abstract = result.select_one('span.abstract-full')
            clean_abstract = abstract.get_text(strip=True).replace("△ Less", "") if abstract else "N/A"
            
            papers.append((clean_title, clean_authors, clean_abstract))
                
        return papers

    async def crawl_all(self) -> List[Tuple[str, str, str]]:
        """Paginated crawling dengan auto-stop"""
        all_papers = []
        start = 0
        page = 1
        
        while True:
            print(f"Mengambil data dari halaman {page}...")
            papers = await self.crawl_page(start)
            
            if not papers:
                print("Tidak ada hasil lagi. Proses dihentikan.")
                break
                
            all_papers.extend(papers)
            start += len(papers)
            page += 1
            
        return all_papers