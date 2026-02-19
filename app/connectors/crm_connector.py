import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

from .base import BaseConnector


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "customers.json"


class CRMConnector(BaseConnector):

    def fetch(self, status: str | None = None, **kwargs) -> List[Dict[str, Any]]:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if status:
            data = [d for d in data if d.get("status") == status]

        return data

    def last_updated(self) -> datetime | None:
        try:
            ts = DATA_PATH.stat().st_mtime
        except OSError:
            return None
        return datetime.fromtimestamp(ts, tz=timezone.utc)

