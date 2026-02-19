"""
Optional demo: LangChain tool calling against this API.

This is NOT required for core API/tests. It demonstrates how an LLM can
select parameters for `/data` via tool calling, then use the API result
to answer the user.

Usage:
  1) Start the API:
       uvicorn app.main:app --reload
  2) Install optional deps:
       pip install langchain langchain-openai requests
  3) Set env vars (or create .env from .env.example):
       OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL (optional)
  4) Run:
       python examples/langchain_tool_calling_demo.py
"""

from __future__ import annotations

import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Literal

import requests

from app.config import settings


API_URL = os.getenv("API_URL", "http://localhost:8000/data")


def fetch_business_data(**params: Any) -> Dict[str, Any]:
    """Tool implementation: call the FastAPI `/data` endpoint."""
    resp = requests.get(API_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _require_env() -> None:
    if not settings.OPENAI_API_KEY or not settings.OPENAI_MODEL:
        raise RuntimeError(
            "Set OPENAI_API_KEY and OPENAI_MODEL (see .env.example)."
        )


def run_langchain_demo(user_query: str) -> None:
    _require_env()

    # Imports kept inside to avoid making LangChain a required dependency.
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    from langchain_core.tools import tool
    from pydantic import BaseModel, Field

    class Source(str, Enum):
        crm = "crm"
        support = "support"
        analytics = "analytics"

    class Order(str, Enum):
        asc = "asc"
        desc = "desc"

    class Priority(str, Enum):
        low = "low"
        medium = "medium"
        high = "high"

    class FetchBusinessDataArgs(BaseModel):
        source: Source = Field(
            ...,
            description="Data source to query. Allowed: crm, support, analytics.",
        )
        page: int = Field(1, ge=1, description="Page number (starts at 1).")
        page_size: int = Field(
            10,
            ge=1,
            le=50,
            description="Requested page size (1-50). Note: API caps to 10 when voice_mode=true.",
        )
        voice_mode: bool = Field(
            True,
            description="If true, applies voice-first constraints (smaller payloads, conservative defaults).",
        )
        summarize: bool = Field(
            False,
            description="If true, returns condensed output optimized for concise responses.",
        )
        status: Optional[str] = Field(
            default=None,
            description="Optional status filter. CRM: active/inactive. Support: open/closed/pending.",
        )
        priority: Optional[Priority] = Field(
            default=None,
            description="Support only. Allowed: low, medium, high.",
        )
        metric: Optional[str] = Field(
            default=None,
            description="Analytics only. Metric name (e.g., daily_active_users).",
        )
        start_date: Optional[str] = Field(
            default=None,
            description="Analytics only. Start date (YYYY-MM-DD) used to filter rows by their `date` field.",
        )
        end_date: Optional[str] = Field(
            default=None,
            description="Analytics only. End date (YYYY-MM-DD) used to filter rows by their `date` field.",
        )
        sort_by: Optional[str] = Field(
            default=None,
            description=(
                "Optional sort field (must be valid for source). "
                "CRM: customer_id, name, email, created_at, status. "
                "Support: ticket_id, customer_id, subject, priority, created_at, status. "
                "Analytics: metric, date, value."
            ),
        )
        order: Order = Field(
            Order.desc,
            description="Sort order. Allowed: asc, desc.",
        )

    @tool("fetch_business_data", args_schema=FetchBusinessDataArgs)
    def fetch_business_data_tool(**kwargs: Any) -> Dict[str, Any]:
        """Retrieve structured business data from CRM, Support, or Analytics."""
        return fetch_business_data(
            **kwargs,
        )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0,
    )

    llm_with_tools = llm.bind_tools([fetch_business_data_tool])

    messages: List[Any] = [
        SystemMessage(
            content=(
                "You are a business data assistant. "
                "Use tools to fetch structured data. "
                "Prefer concise, voice-friendly answers."
            )
        ),
        HumanMessage(content=user_query),
    ]

    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    if not getattr(ai_msg, "tool_calls", None):
        print("\nUser:", user_query)
        print("\nAssistant:", ai_msg.content)
        return

    # Execute tool calls (usually just one)
    for call in ai_msg.tool_calls:
        name = call.get("name")
        args = call.get("args") or {}
        call_id = call.get("id")

        if name != "fetch_business_data":

            continue

        tool_result = fetch_business_data(**args)
        messages.append(
            ToolMessage(
                content=json.dumps(tool_result),
                tool_call_id=call_id,
            )
        )

    final = llm.invoke(messages)

    print("\nUser:", user_query)
    print("\nAssistant:", final.content)


if __name__ == "__main__":
    run_langchain_demo("Show me high priority open support tickets.")
    run_langchain_demo("Give me active customers, most recent first.")

