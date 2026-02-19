from pydantic import BaseModel
from typing import Any, List, Optional


class Metadata(BaseModel):
    total_results: int
    page: int
    page_size: int
    returned_results: int
    total_pages: int
    has_more: bool
    data_freshness: str
    # Optional voice/context helpers
    data_last_updated: Optional[str] = None
    data_staleness_seconds: Optional[int] = None
    voice_hint: Optional[str] = None


class DataResponse(BaseModel):
    source: str
    data_type: str
    data: List[Any]
    metadata: Metadata

