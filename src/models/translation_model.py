"""
TranslationTask model for Multi Translate Service
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as PyEnum
from .base import Base

class TaskStatus(PyEnum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TranslationTask(Base):
    """
    Translation task model
    """
    __tablename__ = "translation_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Task identification
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Input data
    audio_url = Column(Text, nullable=False)
    original_text = Column(Text, nullable=True)
    target_languages = Column(JSON, nullable=False) 
    
    # Task status and tracking
    status = Column(String(50), nullable=False, default=TaskStatus.PENDING.value, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Processing results
    # Speech-to-text result with metadata
    stt_result = Column(JSON, nullable=True)  
    # Translation results for each target language
    translation_results = Column(JSON, nullable=True)  
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TranslationTask(id={self.id}, task_id={self.task_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        try:
            # Safely access all attributes to handle potential lazy loading
            id_value = str(self.id) if hasattr(self, 'id') and self.id is not None else None
            return {
                "id": id_value,
                "task_id": self.task_id,
                "audio_url": self.audio_url,
                "original_text": self.original_text,
                "target_languages": self.target_languages,
                "status": self.status,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "stt_result": self.stt_result,
                "translation_results": self.translation_results,
                "error_message": self.error_message
            }
        except Exception as e:
            # Log the error and return a minimal dict
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in to_dict(): {e}")
            return {
                "task_id": getattr(self, 'task_id', None),
                "status": getattr(self, 'status', None),
                "error": "Failed to serialize task data"
            } 
    

# Supported languages
SUPPORTED_LANGUAGES = [
    'en',      
    'zh-Hans', 
    'zh-Hant', 
    'ja',      
    'ko',      
    'fr',    
    'de',     
    'es',  
    'pt',      
    'ru',    
    'ar',      
    'hi',     
    'it',      
    'nl',      
    'sv',      
]

def validate_languages(languages):
    """Validate target languages"""
    if not languages:
        return False, "Target languages cannot be empty"
    
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            return False, f"Unsupported language: {lang}"
    
    return True, None