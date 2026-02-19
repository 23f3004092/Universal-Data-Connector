from pydantic import BaseModel
from datetime import datetime


class CRMCustomer(BaseModel):
    customer_id: int
    name: str
    email: str
    created_at: datetime
    status: str
