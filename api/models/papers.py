from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import uuid4

class ScrapingRequest(BaseModel):
    query: str = Field(..., description="Search query for ArXiv papers")
    max_results: int = Field(100, description="Maximum number of results to fetch")
    categories: Optional[List[str]] = Field(None, description="ArXiv categories to search in")
    date_from: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    date_to: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    preprocess: bool = Field(True, description="Whether to preprocess the results automatically")

class ScrapingResponse(BaseModel):
    job_id: str
    status: str

class ScrapingStatus(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    request: ScrapingRequest
    progress: Optional[float] = None
    total_items: Optional[int] = None
    processed_items: Optional[int] = None
    results_file: Optional[str] = None
    error: Optional[str] = None

    class Config:
        orm_mode = True

class PaperResponse(BaseModel):
    title: str
    authors: List[str]
    cleaned_title: Optional[str] = None
    cleaned_authors: Optional[List[str]] = None

class VisualizationResponse(BaseModel):
    plot_url: str
    description: str

class EmbeddingResponse(BaseModel):
    paper_id: int
    title: str
    embedding: List[float]