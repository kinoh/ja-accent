#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from text2accent import process_text

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Japanese Accent API",
    description="Convert Japanese text to accent-annotated format for VOICEVOX",
    version="0.1.0",
)

# Configuration from environment variables
MECAB_DICDIR = os.environ.get("MECAB_DICDIR", "/usr/src/app/unidic")
MECAB_USERDIC = os.environ.get("MECAB_USERDIC", "/usr/src/app/user.dic")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests in JSON format"""
    start_time = time.time()

    # Get client IP (handle X-Forwarded-For for proxies)
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    # Process request
    response = await call_next(request)

    # Calculate elapsed time
    elapsed = time.time() - start_time

    # Get request body size from Content-Length header
    body_recv = int(request.headers.get("content-length", 0))

    # Get response body size (stored by Starlette)
    body_sent = 0
    if hasattr(response, "body"):
        body_sent = len(response.body)
    elif "content-length" in response.headers:
        body_sent = int(response.headers["content-length"])

    # Build log entry
    log_entry = {
        "remote_ip": client_ip,
        "time": datetime.now(timezone.utc).isoformat(),
        "request": f"{request.method} {request.url.path}",
        "status": response.status_code,
        "body_recv": body_recv,
        "body_sent": body_sent,
        "referer": request.headers.get("referer", "-"),
        "ua": request.headers.get("user-agent", "-"),
        "elapsed": round(elapsed, 3),
    }

    logger.info(json.dumps(log_entry))

    return response


class AccentRequest(BaseModel):
    text: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "こんにちは、世界。"}
            ]
        }
    }


class AccentResponse(BaseModel):
    accent: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"accent": "コンニチワ'/セ'カイ"}
            ]
        }
    }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Japanese Accent API is running"}


@app.post("/accent", response_model=AccentResponse)
async def convert_accent(request: AccentRequest) -> AccentResponse:
    """Convert Japanese text to accent-annotated format.

    Args:
        request: Request containing Japanese text

    Returns:
        Response containing accent-annotated text

    Raises:
        HTTPException: If text processing fails
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        result = process_text(request.text, MECAB_DICDIR, MECAB_USERDIC)
        return AccentResponse(accent=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
