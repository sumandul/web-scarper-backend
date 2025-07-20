from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal, Dict, Any


# ✅ Request model when starting a new scrape
class ScrapeRequest(BaseModel):
    url: HttpUrl
    scraper_type: Optional[Literal["beautifulsoup", "playwright"]] = "beautifulsoup"
    tags: Optional[List[str]] = []


# ✅ Response model after a job is created
class ScrapeResponse(BaseModel):
    job_id: str
    status: str
    data: Dict[str, Any]


# ✅ Detailed model to return enriched job data
class ScrapeJobOut(BaseModel):
    id: str
    url: str
    scraper_type: str
    status: str

    # Content
    raw_html: Optional[str] = None
    llm_summary: Optional[str] = None
    headline: Optional[str] = None
    tldr: Optional[str] = None

    # AI Enrichment
    topics: Optional[List[str]] = []
    seo_tags: Optional[List[str]] = []
    entities: Optional[Dict[str, List[str]]] = {}
    sentiment: Optional[str] = None
    tags: Optional[List[str]] = []

    created_at: Optional[str] = None

    class Config:
        orm_mode = True
