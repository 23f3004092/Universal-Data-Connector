import random
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any


def generate_customers(n: int = 30) -> List[Dict[str, Any]]:
    statuses = ["active", "inactive"]
    now = datetime.now(timezone.utc)
    return [
        {
            "customer_id": i,
            "name": f"Customer {i}",
            "email": f"user{i}@example.com",
            "created_at": (now - timedelta(days=random.randint(1, 365))).isoformat(),
            "status": random.choice(statuses),
        }
        for i in range(1, n + 1)
    ]


def generate_support_tickets(n: int = 50) -> List[Dict[str, Any]]:
    statuses = ["open", "closed", "pending"]
    priorities = ["low", "medium", "high"]
    now = datetime.now(timezone.utc)

    return [
        {
            "ticket_id": i,
            "customer_id": random.randint(1, 50),
            "subject": f"Issue {i}",
            "status": random.choice(statuses),
            "priority": random.choice(priorities),
            "created_at": (now - timedelta(days=random.randint(0, 30))).isoformat(),
        }
        for i in range(1, n + 1)
    ]


def generate_analytics_metrics(metric: str = "daily_active_users", days: int = 30) -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "metric": metric,
            "date": (today - timedelta(days=i)).isoformat(),
            "value": random.randint(100, 1000),
        }
        for i in range(days)
    ]
