
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List


def summarize_for_voice(source: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reduce payload size for voice/low-bandwidth responses while keeping
    fields that preserve identity + recency + actionability.
    """
    summarized: List[Dict[str, Any]] = []

    for item in data:
        reduced_item: Dict[str, Any] = {}

        if source == "crm":
            for key in ["customer_id", "name", "status", "created_at", "email"]:
                if key in item:
                    reduced_item[key] = item[key]

        elif source == "support":
            for key in [
                "ticket_id",
                "subject",
                "priority",
                "status",
                "created_at",
                "customer_id",
            ]:
                if key in item:
                    reduced_item[key] = item[key]

        elif source == "analytics":
            # keep canonical time-series keys
            for key in ["metric", "date", "value"]:
                if key in item:
                    reduced_item[key] = item[key]
            # Normalize date to ISO for consistent voice reading
            if isinstance(reduced_item.get("date"), date):
                reduced_item["date"] = reduced_item["date"].isoformat()

        else:
            # fallback: keep a small, stable subset
            for key in list(item.keys())[:6]:
                reduced_item[key] = item[key]

        summarized.append(reduced_item)

    return summarized
