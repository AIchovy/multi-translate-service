"""
Text schemas
"""

from typing import Optional
from pydantic import BaseModel, Field

class TextQueryParams(BaseModel):
    language: str = Field(..., description="Language code")
    text_id: str = Field(..., description="Text id")
    source: Optional[str] = Field(None, description="Source")