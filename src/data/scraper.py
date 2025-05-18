import arxiv
import asyncio
import time
from typing import List, Dict, Optional
import re

class ArXivScraper:
    def __init__(self):
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=3.0,
            num_retries=5
        )
        
    async def search_papers(self, query="MIT", max_results=None, 
                           categories=None, date_from=None, date_to=None):
        search_query = query
        
        if categories and isinstance(categories, list) and len(categories) > 0:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({search_query}) AND ({cat_query})"
        
        date_filters = []
        if date_from:
            try:
                date_filters.append(f"submittedDate:[{date_from}0000 TO *]")
            except:
                pass
        
        if date_to:
            try:
                date_filters.append(f"submittedDate:[* TO {date_to}2359]")
            except:
                pass
        
        if date_filters:
            date_query = " AND ".join(date_filters)
            search_query = f"({search_query}) AND ({date_query})"
        
        if max_results is None or max_results <= 0:
            max_results = 10000  
            
        print(f"Mencari paper dengan query: '{search_query}'")
        
        return await asyncio.to_thread(self._fetch_papers, search_query, max_results)
        
    def _fetch_papers(self, search_query, max_results):
        """
        Mengambil paper dari API ArXiv
        """
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            print("Mengambil paper dari ArXiv API...")
            
            papers = []
            for i, result in enumerate(self.client.results(search)):
                paper_dict = {
                    "Title": result.title.replace("\n", " ").strip(),
                    "Authors": ", ".join([author.name for author in result.authors]),
                    "Abstract": result.summary.replace("\n", " ").strip(),
                    "Journal_Conference_Name": result.journal_ref if hasattr(result, 'journal_ref') and result.journal_ref else "N/A",
                    "Publisher": "arXiv",
                    "Year": self._extract_year(result.published) if hasattr(result, 'published') else "N/A",
                    "DOI": result.doi if hasattr(result, 'doi') and result.doi else "N/A",
                    "Group_Name": result.primary_category if hasattr(result, 'primary_category') else "N/A"
                }
                
                papers.append(paper_dict)
                
                if (i+1) % 100 == 0:
                    print(f"Telah mengambil {i+1} paper...")
                
                if i+1 >= max_results:
                    break
                    
                if (i+1) % 50 == 0:
                    time.sleep(1)
            
            print(f"Berhasil mengambil {len(papers)} paper dari ArXiv API")
            return papers
            
        except Exception as e:
            print(f"Error mengambil paper: {str(e)}")
            time.sleep(10)
            try:
                print("Mencoba kembali...")
                papers = []
                for result in self.client.results(search):
                    paper_dict = {
                        "Title": result.title.replace("\n", " ").strip(),
                        "Authors": ", ".join([author.name for author in result.authors]),
                        "Abstract": result.summary.replace("\n", " ").strip(),
                        "Journal_Conference_Name": result.journal_ref if hasattr(result, 'journal_ref') and result.journal_ref else "N/A",
                        "Publisher": "arXiv",
                        "Year": self._extract_year(result.published) if hasattr(result, 'published') else "N/A",
                        "DOI": result.doi if hasattr(result, 'doi') and result.doi else "N/A",
                        "Group_Name": result.primary_category if hasattr(result, 'primary_category') else "N/A"
                    }
                    papers.append(paper_dict)
                    
                    if len(papers) >= max_results:
                        break
                
                return papers
            except Exception as e:
                print(f"Gagal mengambil paper setelah percobaan ulang: {str(e)}")
                return []
    
    def _extract_year(self, published_date):
        """Ekstrak tahun dari tanggal publikasi"""
        if published_date:
            year_match = re.search(r'(\d{4})', str(published_date))
            if year_match:
                return year_match.group(1)
        return "N/A"
    
    async def crawl_papers(self, query="MIT", max_results=None, categories=None, 
                          date_from=None, date_to=None) -> List[Dict]:
        """Ambil paper dari ArXiv API"""
        print(f"Mengambil data dengan query: {query}, max_results: {max_results if max_results else 'ALL'}...")
        
        papers = await self.search_papers(
            query=query, 
            max_results=max_results, 
            categories=categories,
            date_from=date_from,
            date_to=date_to
        )
        
        print(f"Total berhasil mengambil {len(papers)} paper")
        return papers