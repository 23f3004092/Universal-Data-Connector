from pydantic import BaseModel
from datetime import datetime


class SupportTicket(BaseModel):
    ticket_id: int
    customer_id: int
    subject: str
    priority: str
    created_at: datetime
    status: str
