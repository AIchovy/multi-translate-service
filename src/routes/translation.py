"""
Translation routes module for Multi Translate Service
"""

from fastapi import APIRouter, Depends
from src.schemas.text_schemas import TextQueryParams
from src.schemas.translation_schemas import TranslationParams
from src.services.file_decoding_service import FileDecodingService
from src.services.translation_services import TranslationService
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.config import settings
from src.utils.logger import get_logger
from src.models.base import get_db

# Get logger for this module
logger = get_logger(__name__)

router = APIRouter()

# Create translation task
@router.post("/translation_task")
async def create_task(task: TranslationParams, db: AsyncSession = Depends(get_db)):
    """Create a new translation task"""
    task_result = await TranslationService.create_task(db, task)
    logger.info(f"Creating translation task: {task_result['task_id']}")

    return {"status": "ok", "data": {"task_id": task_result["task_id"]}}

# Get task status
@router.get("/translation_task/{task_id}")
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get task status"""
    task = await TranslationService.get_task(db, task_id)
    return {"status": "ok", "data": task}

# Cancel task
@router.post("/translation_task/{task_id}/cancel")
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel task"""
    result = await TranslationService.cancel_task(db, task_id)
    return {"status": "ok", "data": result}

@router.post("/query_text")
async def query_text(params: TextQueryParams, db: AsyncSession = Depends(get_db)):
    """Query text"""
    file_decoding_service = FileDecodingService()
    text = file_decoding_service.get_text(params.language, params.text_id, params.source)
    return {"status": "ok", "data": text}

# Health check
@router.get("/health")
async def health_check():
    """Health check API"""
    logger.info("Executing health check...")
    return {"status": "ok", "data": {"environment": settings.environment}} 