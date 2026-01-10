#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from text2accent import process_text

app = FastAPI(
    title="Japanese Accent API",
    description="Convert Japanese text to accent-annotated format for VOICEVOX",
    version="0.1.0",
)

# Configuration from environment variables
MECAB_DICDIR = os.environ.get("MECAB_DICDIR", "/usr/src/app/unidic")
MECAB_USERDIC = os.environ.get("MECAB_USERDIC", "/usr/src/app/user.dic")


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
