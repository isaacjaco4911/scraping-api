from pydantic import BaseModel
from typing import List, Optional, Dict


class ScrapeRequest(BaseModel):
    url: str

    model_config = {
        "json_schema_extra": {
            "example": {"url": "https://quotes.toscrape.com"}
        }
    }


class ImageData(BaseModel):
    src: str
    alt: str


class ScrapeResponse(BaseModel):
    url: str
    status_code: int
    response_time_ms: float
    title: Optional[str]
    meta_description: Optional[str]
    headings: Dict[str, List[str]]
    paragraphs: List[str]
    links: List[str]
    images: List[ImageData]
    price: Optional[str]
    scraped_at: str
