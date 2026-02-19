from app.services.business_rules import (
    enforce_page_size,
    paginate,
)
from app.config import settings


def test_enforce_page_size_caps_max():
    oversized = settings.MAX_PAGE_SIZE + 100
    assert enforce_page_size(oversized) == settings.MAX_PAGE_SIZE


def test_enforce_page_size_valid():
    assert enforce_page_size(5) == 5


def test_paginate_basic():
    data = [{"id": i} for i in range(20)]

    paginated, total, total_pages, has_more = paginate(
        data,
        page=1,
        page_size=5
    )

    assert len(paginated) == 5
    assert total == 20
    assert total_pages == 4
    assert has_more is True


def test_paginate_last_page():
    data = [{"id": i} for i in range(10)]

    paginated, total, total_pages, has_more = paginate(
        data,
        page=2,
        page_size=5
    )

    assert len(paginated) == 5
    assert has_more is False

