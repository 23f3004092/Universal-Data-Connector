from typing import List, Dict, Any, Tuple
from math import ceil
from app.config import settings


def enforce_page_size(page_size: int) -> int:
    if page_size > settings.MAX_PAGE_SIZE:
        return settings.MAX_PAGE_SIZE
    return page_size


def paginate(
    data: List[Dict[str, Any]],
    page: int,
    page_size: int,
) -> Tuple[List[Dict[str, Any]], int, int, bool]:

    total = len(data)
    total_pages = ceil(total / page_size) if total > 0 else 1

    start = (page - 1) * page_size
    end = start + page_size

    paginated_data = data[start:end]
    has_more = page < total_pages

    return paginated_data, total, total_pages, has_more


def should_summarize(summarize: bool) -> bool:
    return summarize
