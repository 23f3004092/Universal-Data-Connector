import json
from pathlib import Path
from datetime import date, datetime, timezone
from typing import List, Dict, Any

from .base import BaseConnector


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "analytics.json"


class AnalyticsConnector(BaseConnector):

    def fetch(
        self,
        metric: str | None = None,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if metric:
            data = [d for d in data if d.get("metric") == metric]

        # Optional ISO date-range filtering (YYYY-MM-DD)
        if start_date or end_date:
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)

            def within_range(d: Dict[str, Any]) -> bool:
                try:
                    d_date = date.fromisoformat(str(d.get("date")))
                except Exception:
                    return False
                if start_date and d_date < start_date:
                    return False
                if end_date and d_date > end_date:
                    return False
                return True

            data = [d for d in data if within_range(d)]

        return data

    def last_updated(self) -> datetime | None:
        try:
            ts = DATA_PATH.stat().st_mtime
        except OSError:
            return None
        return datetime.fromtimestamp(ts, tz=timezone.utc)
