# Universal Data Connector (FastAPI)

Production-style **Universal Data Connector** that exposes a unified `/data` API for CRM, Support Tickets, and Analytics data sources, designed for **LLM function-calling** and **voice-first** responses (small payloads, helpful metadata).

## Requirements

- Python **3.11+**

## Setup (local)

### 1) Create a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### Optional demo dependencies

```bash
pip install -r requirements-optional.txt
```

### 3) Environment variables (optional)

This project does **not** require an API key to run the API or tests.

- Copy `.env.example` → `.env` only if you want to run optional LLM demo scripts.

## Run the API

```bash
uvicorn app.main:app --reload
```

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## API usage

### Fetch CRM records

```bash
curl "http://localhost:8000/data?source=crm"
```

### Fetch open, high-priority support tickets (paged)

```bash
curl "http://localhost:8000/data?source=support&status=open&priority=high&page=1&page_size=10"
```

### Fetch analytics time-series for a metric (optionally date-filtered)

```bash
curl "http://localhost:8000/data?source=analytics&metric=daily_active_users&start_date=2026-02-10&end_date=2026-02-16"
```

### Voice-first behavior

- `voice_mode=true` (default) caps `page_size` to **10**.
- If `sort_by` is omitted, results are prioritized by recency (`created_at` or `date`, descending).
- `summarize=true` returns source-aware condensed records.

## Run tests

### Run the full test suite

```bash
pytest -q
```

### Run a single test file

```bash
pytest -q tests/test_api.py
```

## Run with Docker

```bash
docker-compose up --build
```

Then open `http://localhost:8000/docs`.

## Optional: LLM tool-calling demo

This is **optional** and not required for core functionality or tests.

1) Start the API

```bash
uvicorn app.main:app --reload
```

2) Install optional packages

```bash
pip install openai requests
```

3) Set environment variables (or create `.env` from `.env.example`)

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL` (optional)

4) Run the demo

```bash
python examples/openai_tool_calling_demo.py
```

## Optional: LangChain tool-calling demo

This is **optional** and not required for core functionality or tests.

1) Start the API

```bash
uvicorn app.main:app --reload
```

2) Install optional packages

```bash
pip install langchain langchain-openai requests
```

3) Set environment variables (or create `.env` from `.env.example`)

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL` (optional)

4) Run the demo

```bash
python examples/langchain_tool_calling_demo.py
```



