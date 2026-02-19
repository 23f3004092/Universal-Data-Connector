

from fastapi import APIRouter, Query, HTTPException
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.connectors.analytics_connector import AnalyticsConnector

from app.models.common import DataResponse, Metadata
from app.services.data_identifier import identify_data_type
from app.services.business_rules import (
    enforce_page_size,
    paginate,
    should_summarize,
)
from app.services.voice_optimizer import summarize_for_voice
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

router = APIRouter(tags=["Universal Data Connector"])


# -----------------------
# ENUMS
# -----------------------

class DataSource(str, Enum):
    crm = "crm"
    support = "support"
    analytics = "analytics"

    @classmethod
    def _missing_(cls, value):
        # Accept case-insensitive inputs like "Support" from LLMs.
        if isinstance(value, str):
            normalized = value.strip().lower()
            for member in cls:
                if member.value == normalized:
                    return member
        return None


# -----------------------
# CONNECTOR MAP
# -----------------------

connector_map = {
    DataSource.crm: CRMConnector(),
    DataSource.support: SupportConnector(),
    DataSource.analytics: AnalyticsConnector(),
}


# -----------------------
# SOURCE FIELD DEFINITIONS
# -----------------------

SOURCE_ALLOWED_FILTERS = {
    DataSource.crm: {"status"},
    DataSource.support: {"status", "priority"},
    DataSource.analytics: {"metric", "start_date", "end_date"},
}

SOURCE_ALLOWED_SORT_FIELDS = {
    DataSource.crm: {"customer_id", "name", "email", "created_at", "status"},
    DataSource.support: {
        "ticket_id",
        "customer_id",
        "subject",
        "priority",
        "created_at",
        "status",
    },
    DataSource.analytics: {"metric", "date", "value"},
}


# -----------------------
# ROUTE
# -----------------------

@router.get(
    "/data",
    response_model=DataResponse,
    summary="Fetch structured business data",
    description="""
Retrieve structured business data from CRM, Support, or Analytics systems.

Each source supports specific filters and sorting fields.

Source-specific filters:
- CRM → status
- Support → status, priority
- Analytics → metric
"""
)
async def get_data(
    source: DataSource = Query(
        ...,
        description="Data source to query: crm, support, analytics."
    ),

    page: int = Query(
        1,
        ge=1,
        description="Page number (starts from 1)."
    ),

    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description=f"Number of records per page (max {settings.MAX_PAGE_SIZE})."
    ),

    voice_mode: bool = Query(
        True,
        description="If true, applies voice-first constraints (smaller payloads, conservative defaults can cap the page_size to 10 irrespective of the page_size parameter).",
    ),

    summarize: bool = Query(
        False,
        description="If true, returns condensed output optimized for concise responses."
    ),

    status: Optional[str] = Query(
        None,
        description="Status filter (CRM: active/inactive, Support: open/closed/pending)."
    ),

    priority: Optional[str] = Query(
        None,
        description="Support tickets only: priority filter (low, medium, high)."
    ),

    metric: Optional[str] = Query(
        None,
        description="Analytics only: metric name filter (e.g., revenue, daily_active_users)."
    ),

    start_date: Optional[str] = Query(
        None,
        description="Analytics only: start date (YYYY-MM-DD) for time-series filtering.",
    ),

    end_date: Optional[str] = Query(
        None,
        description="Analytics only: end date (YYYY-MM-DD) for time-series filtering.",
    ),

    sort_by: Optional[str] = Query(
        None,
        description=(
            "Field name to sort results by (must be valid for selected source). "
            "Allowed values: "
            "CRM → customer_id, name, email, created_at, status; "
            "Support → ticket_id, customer_id, subject, priority, created_at, status; "
            "Analytics → metric, date, value."
        ),
    ),

    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Sorting order: asc or desc."
    ),
):

    logger.info(f"Incoming request | source={source}")

    connector = connector_map.get(source)
    if not connector:
        raise HTTPException(status_code=400, detail="Invalid data source.")

    # -----------------------
    # VALIDATE FILTERS
    # -----------------------

    provided_filters = {
        "status": status,
        "priority": priority,
        "metric": metric,
        "start_date": start_date,
        "end_date": end_date,
    }

    allowed_filters = SOURCE_ALLOWED_FILTERS[source]

    for key, value in provided_filters.items():
        if value is not None and key not in allowed_filters:
            raise HTTPException(
                status_code=400,
                detail=f"Filter '{key}' is not allowed for source '{source.value}'."
            )

    # -----------------------
    # FETCH DATA
    # -----------------------

    raw_data = connector.fetch(
        status=status,
        priority=priority,
        metric=metric,
        start_date=start_date,
        end_date=end_date,
    )

    # -----------------------
    # SORTING (default prioritization for voice)
    # -----------------------

    allowed_sort_fields = SOURCE_ALLOWED_SORT_FIELDS[source]

    if sort_by is not None:
        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot sort by '{sort_by}' for source '{source.value}'."
            )

        sort_key = sort_by
        sort_order = order
    else:
        # Default prioritization: most recent first when available
        if source == DataSource.analytics:
            sort_key = "date"
        else:
            sort_key = "created_at"
        sort_order = "desc"

    if sort_key in allowed_sort_fields:
        raw_data = sorted(
            raw_data,
            key=lambda x: x.get(sort_key) or "",
            reverse=(sort_order == "desc"),
        )

    # -----------------------
    # PAGINATION (voice-first constraints)
    # -----------------------

    page_size = enforce_page_size(page_size)
    if voice_mode:
        page_size = min(page_size, settings.DEFAULT_PAGE_SIZE)

    paginated_data, total, total_pages, has_more = paginate(
        raw_data,
        page,
        page_size,
    )

    # -----------------------
    # OPTIONAL SUMMARIZATION
    # -----------------------

    if should_summarize(summarize):
        paginated_data = summarize_for_voice(source.value, paginated_data)

    # -----------------------
    # RESPONSE
    # -----------------------

    last_updated = connector.last_updated()
    staleness_seconds: int | None = None
    last_updated_iso: str | None = None
    if last_updated:
        last_updated_iso = last_updated.isoformat()
        staleness_seconds = int((datetime.now(timezone.utc) - last_updated).total_seconds())

    metadata = Metadata(
        total_results=total,
        page=page,
        page_size=page_size,
        returned_results=len(paginated_data),
        total_pages=total_pages,
        has_more=has_more,
        data_freshness=datetime.now(timezone.utc).isoformat(),
        data_last_updated=last_updated_iso,
        data_staleness_seconds=staleness_seconds,
        voice_hint=f"Showing {len(paginated_data)} of {total} results",
    )

    return DataResponse(
        source=source.value,
        data_type=identify_data_type(raw_data),
        data=paginated_data,
        metadata=metadata,
    )
