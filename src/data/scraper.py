import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional

class ArXivScraper:
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None

    async def crawl_page(self, start: int, size: int = 200) -> Optional[List[str]]:
        """Crawl individual arXiv page"""
        url = f"https://arxiv.org/search/?query=MIT&searchtype=all&abstracts=show&order=-announced_date_first&size={size}&date-date_type=submitted_date&start={start}"
        html = await self.fetch_page(url)
        
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        results_message = soup.select_one('h1.title.is-clearfix')
        
        if results_message and "No results" in results_message.text:
            return []
            
        return [
            tag.get_text(strip=True).replace("Title:", "")
            for tag in soup.select('li.arxiv-result p.title.is-5.mathjax')
        ]

    async def crawl_all(self) -> List[str]:
        """Paginated crawling with auto-stop"""
        all_titles = []
        start = 0
        page = 1
        
        while True:
            titles = await self.crawl_page(start)
            
            if not titles:
                print("Tidak ada hasil lagi. Proses dihentikan.")
                break
                
            all_titles.extend(titles)
            print(f"Mengambil data dari halaman {page} ditemukan {len(titles)} judul...")
            
            start += len(titles)
            page += 1
            
        return all_titles