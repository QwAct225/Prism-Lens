import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urljoin

class ArXivScraper:
    BASE_URL = "https://arxiv.org/search/?query=MIT&searchtype=all&abstracts=show&order=-announced_date_first&size=200&date-date_type=submitted_date&start=0"
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    print(f"Error fetching {url}: Status {response.status}")
                    return None
            except Exception as e:
                print(f"Exception while fetching {url}: {e}")
                return None

    async def get_paper_links(self, start: int, size: int = 200) -> Optional[List[Tuple[str, str, str]]]:
        """Get links to individual paper pages from search results"""
        url = f"https://arxiv.org/search/?query=MIT&searchtype=all&abstracts=show&order=-announced_date_first&size={size}&date-date_type=submitted_date&start={start}"
        html = await self.fetch_page(url)
        
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        results_message = soup.select_one('h1.title.is-clearfix')
        
        if results_message and "No results" in results_message.text:
            return []
            
        paper_links = []
        for result in soup.select('li.arxiv-result'):
            link_elem = result.select_one('p.list-title.is-inline-block a[href*="/abs/"]')
            if link_elem and link_elem.get('href'):
                paper_links.append(urljoin(self.BASE_URL, link_elem.get('href')))
                
        return paper_links

    async def extract_paper_details(self, paper_url: str) -> Optional[Dict]:
        """Extract all required details from individual paper page"""
        html = await self.fetch_page(paper_url)
        
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        title_elem = soup.select_one('h1.title')
        title = title_elem.get_text(strip=True).replace("Title:", "") if title_elem else "N/A"
        
        authors_elem = soup.select_one('div.authors')
        authors = []
        if authors_elem:
            author_links = authors_elem.select('a[href*="searchtype=author"]')
            authors = [a.get_text(strip=True) for a in author_links]
        
        abstract_elem = soup.select_one('blockquote.abstract')
        abstract = abstract_elem.get_text(strip=True).replace("Abstract:", "") if abstract_elem else "N/A"
        
        journal_elem = soup.select_one('td.tablecell:-soup-contains("Journal ref:")')
        journal = journal_elem.find_next_sibling('td').get_text(strip=True) if journal_elem else "N/A"
        
        publisher = "arXiv"
        breadcrumbs = soup.select_one('div.header-breadcrumbs')
        if breadcrumbs:
            breadcrumb_text = breadcrumbs.get_text(strip=True)
            if "arXiv:" in breadcrumb_text:
                publisher = "arXiv"
        
        year = "N/A"
        date_elem = soup.select_one('div.dateline')
        if date_elem:
            date_match = re.search(r'\d{1,2} [A-Za-z]+ (\d{4})', date_elem.get_text())
            if date_match:
                year = date_match.group(1)
        
        doi = "N/A"
        doi_elem = soup.select_one('a#arxiv-doi-link')
        if doi_elem:
            doi = doi_elem.get_text(strip=True)
        
        group_name = "N/A"
        subject_elem = soup.select_one('span.primary-subject')
        if subject_elem:
            group_name = subject_elem.get_text(strip=True)
        
        return {
            "Title": title,
            "Authors": ", ".join(authors),
            "Abstract": abstract,
            "Journal_Conference_Name": journal,
            "Publisher": publisher,
            "Year": year,
            "DOI": doi,
            "Group_Name": group_name
        }

    async def crawl_papers(self) -> List[Tuple[str, str, str]]:
        """Crawl semua paper tanpa batas"""
        all_papers = []
        start = 0
        page = 1
        
        while True:
            print(f"Mengambil data dari halaman {page}...")
            paper_links = await self.get_paper_links(start)
            
            if not paper_links:
                print("Tidak ada hasil lagi. Proses dihentikan.")
                break
                
            tasks = [self.extract_paper_details(link) for link in paper_links]
            results = await asyncio.gather(*tasks)
            
            valid_papers = [paper for paper in results if paper is not None]
            all_papers.extend(valid_papers)
            
            print(f"Berhasil mengambil {len(valid_papers)} paper dari halaman {page}")
            
            start += 200 
            page += 1
            
            await asyncio.sleep(3)
            
        return all_papers