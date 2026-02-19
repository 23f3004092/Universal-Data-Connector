
from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import health, data
from app.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("app")

app = FastAPI(title="Universal Data Connector")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.exception(
                f"Unhandled error | request_id={request_id} | {request.method} {request.url.path} | {duration_ms}ms"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id,
                },
            )

        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            f"Request | request_id={request_id} | {request.method} {request.url.path} | {response.status_code} | {duration_ms}ms"
        )
        response.headers["x-request-id"] = request_id
        return response


app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Compact validation error shape; includes request path for debugging.
    logger.warning(f"Validation error | {request.method} {request.url.path} | {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.include_router(health.router)
app.include_router(data.router)
