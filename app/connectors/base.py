
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class BaseConnector(ABC):

    @abstractmethod
    def fetch(self, **filters) -> List[Dict[str, Any]]:
        pass

    def last_updated(self) -> Optional[datetime]:
        """
        Best-effort timestamp indicating when the underlying datasource last changed.
        Used for freshness/staleness indicators in voice contexts.
        """
        return None

