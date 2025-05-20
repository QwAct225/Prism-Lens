import arxiv
import asyncio
import time
from typing import List, Dict, Optional
import re
from prometheus_client import Counter, Histogram, Gauge

class ArXivScraper:
    def __init__(self):
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=3.0,
            num_retries=5
        )
        
        # Initialize Prometheus metrics
        self.request_count = Counter(
            'arxiv_requests_total', 
            'Total count of requests made to ArXiv API',
            ['query_type', 'status']
        )
        
        self.papers_retrieved = Counter(
            'arxiv_papers_retrieved_total',
            'Total number of papers retrieved from ArXiv'
        )
        
        self.request_latency = Histogram(
            'arxiv_request_duration_seconds',
            'Histogram of request latencies',
            ['query_type'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf'))
        )
        
        self.error_count = Counter(
            'arxiv_request_errors_total',
            'Total count of errors encountered during ArXiv requests',
            ['error_type']
        )
        
        self.active_requests = Gauge(
            'arxiv_active_requests',
            'Number of currently active ArXiv requests'
        )
        
        # Add a paper count gauge for current scrape operation
        self.current_paper_count = Gauge(
            'arxiv_current_papers_count',
            'Number of papers in the current scraping operation'
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
        
        self.active_requests.inc()
        start_time = time.time()
        try:
            papers = await asyncio.to_thread(self._fetch_papers, search_query, max_results)
            self.request_count.labels(query_type='search', status='success').inc()
            return papers
        except Exception as e:
            self.request_count.labels(query_type='search', status='error').inc()
            self.error_count.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            self.active_requests.dec()
            self.request_latency.labels(query_type='search').observe(time.time() - start_time)
        
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
                
                # Update paper count for each paper - increment individually
                self.papers_retrieved.inc()
                
                if (i+1) % 100 == 0:
                    print(f"Telah mengambil {i+1} paper...")
                
                if i+1 >= max_results:
                    break
                    
                if (i+1) % 50 == 0:
                    time.sleep(1)
            
            print(f"Berhasil mengambil {len(papers)} paper dari ArXiv API")
            print(f"Total papers retrieved metric should be: {len(papers)}")
            return papers
            
        except Exception as e:
            print(f"Error mengambil paper: {str(e)}")
            self.error_count.labels(error_type=type(e).__name__).inc()
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
                
                print(f"Recovered {len(papers)} papers after retry")
                self.papers_retrieved.inc(len(papers))
                return papers
            except Exception as e:
                print(f"Gagal mengambil paper setelah percobaan ulang: {str(e)}")
                self.error_count.labels(error_type=type(e).__name__).inc()
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
        
        start_time = time.time()
        self.active_requests.inc()
        
        try:
            papers = await self.search_papers(
                query=query, 
                max_results=max_results, 
                categories=categories,
                date_from=date_from,
                date_to=date_to
            )
            
            print(f"Total berhasil mengambil {len(papers)} paper")
            self.request_count.labels(query_type='crawl', status='success').inc()
            return papers
        except Exception as e:
            self.request_count.labels(query_type='crawl', status='error').inc()
            self.error_count.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            self.active_requests.dec()
            self.request_latency.labels(query_type='crawl').observe(time.time() - start_time)
            print(f"Request latency observed: {time.time() - start_time} seconds")