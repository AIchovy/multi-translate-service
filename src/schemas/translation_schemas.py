"""
Translation schemas module for Multi Translate Service
"""

from pydantic import BaseModel, Field
from typing import Optional

class TranslationParams(BaseModel):
    audio_url: str = Field(..., min_length=1, strip_whitespace=True, description="Audio URL is required and cannot be empty or whitespace")
    original_text: Optional[str] = None
    target_languages: list[str] = Field(..., min_items=1, description="Target languages list cannot be empty")