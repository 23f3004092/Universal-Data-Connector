from pydantic import BaseModel
from datetime import date


class AnalyticsMetric(BaseModel):
    metric: str
    date: date
    value: int
