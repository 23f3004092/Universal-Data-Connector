"""
Optional demo: OpenAI-style function calling + this API.

Not required for core assignment tests.

Usage:
  1) Start the API:
       uvicorn app.main:app --reload
  2) Set env vars (or create .env):
       OPENAI_API_KEY, OPENAI_BASE_URL (optional), OPENAI_MODEL
  3) Run:
       python examples/openai_tool_calling_demo.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests
from openai import OpenAI

from app.config import settings


API_URL = os.getenv("API_URL", "http://localhost:8000/data")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_business_data",
            "description": "Retrieve structured data from CRM, Support, or Analytics systems.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["crm", "support", "analytics"]},
                    "page": {"type": "integer", "minimum": 1},
                    "page_size": {"type": "integer", "minimum": 1, "maximum": 50},
                    "voice_mode": {"type": "boolean"},
                    "summarize": {"type": "boolean"},
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "metric": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "sort_by": {
                        "type": "string",
                        "description": (
                            "Sort field. Allowed values depend on source: "
                            "CRM: customer_id, name, email, created_at, status; "
                            "Support: ticket_id, customer_id, subject, priority, created_at, status; "
                            "Analytics: metric, date, value."
                        ),
                    },
                    "order": {"type": "string", "enum": ["asc", "desc"]},
                },
                "required": ["source"],
            },
        },
    }
]


def call_api(params: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.get(API_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def run_llm_query(user_query: str) -> None:
    if not settings.OPENAI_API_KEY or not settings.OPENAI_MODEL:
        raise RuntimeError(
            "Set OPENAI_API_KEY and OPENAI_MODEL (see .env.example)."
        )

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Choose correct parameters to retrieve structured business data.",
            },
            {"role": "user", "content": user_query},
        ],
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = response.choices[0].message
    if not msg.tool_calls:
        print("\nUser:", user_query)
        print("Assistant: (no tool call)")
        return

    tool_call = msg.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    print("\nUser:", user_query)
    print("\nTool args:\n", json.dumps(args, indent=2))
    print("\nAPI response:\n", json.dumps(call_api(args), indent=2))


if __name__ == "__main__":
    run_llm_query("Show me high priority open support tickets.")
    run_llm_query("Give me active customers, most recent first.")
    run_llm_query("What are the daily active users for the last 7 days?")

