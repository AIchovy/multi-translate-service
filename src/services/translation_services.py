"""
Translation service module for Multi Translate Service
"""

from datetime import datetime, timezone
from fastapi import HTTPException
import uuid
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from celery.result import AsyncResult

from src.celery_app import celery_app
from src.models.translation_model import TranslationTask, TaskStatus, validate_languages
from src.schemas.translation_schemas import TranslationParams
from src.utils.logger import get_logger
from src.tasks.translation_tasks import stt_task


logger = get_logger(__name__)

class TranslationService:
    """Service for handling translation tasks"""
    
    @staticmethod
    async def create_task(db: AsyncSession, params: TranslationParams) -> Dict[str, Any]:
        """
        Create a new translation task
        
        Args:
            db: Database session
            params: Translation parameters
            
        Returns:
            Dictionary with task information
        """
        # check target languages
        is_valid, error_message = validate_languages(params.target_languages)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # check audio url
        if not params.audio_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Audio URL must be a valid HTTP/HTTPS URL")
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Create new translation task
        task = TranslationTask(
            task_id=task_id,
            audio_url=params.audio_url,
            original_text=params.original_text,
            target_languages=params.target_languages,
            status=TaskStatus.PENDING.value
        )
        
        # Add to database 
        db.add(task)
        
        # Trigger task AFTER database commit to avoid race condition
        try:
            stt_task.apply_async(args=[task_id], task_id=task_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to trigger STT task for {task_id}: {e}")
            raise 
        
        logger.info(f"Created translation task: {task_id}")
        
        result = task.to_dict()
        return result
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        result = await db.execute(
            select(TranslationTask).filter(TranslationTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Eagerly load all attributes to avoid lazy loading issues
        await db.refresh(task)
        # Check celery task status with task_id
        celery_result = AsyncResult(task_id, app=celery_app)

        logger.info(f"Task {task_id} Celery result state: {celery_result.state}")

        # Sync status 
        needs_update = False
        updated_status = task.status
        error_message = task.error_message
        
        try:
            if celery_result.state == 'FAILURE':
                # Celery task failed
                if task.status not in [TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                    updated_status = TaskStatus.FAILED.value
                    error_message = str(celery_result.info) if celery_result.info else "Task failed in Celery"
                    needs_update = True
                    logger.warning(f"Syncing failed task status for {task_id}: {error_message}")
            
            elif celery_result.state == 'SUCCESS':
                # Celery task succeeded but DB might not be updated
                if task.status not in [TaskStatus.COMPLETED.value]:
                    updated_status = TaskStatus.COMPLETED.value
                    needs_update = True
                    logger.warning(f"Syncing completed task status for {task_id}")
                    
            elif celery_result.state == 'PENDING':
                # Task not started or doesn't exist in Celery
                if task.status == TaskStatus.PROCESSING.value:
                    # Task was processing but Celery doesn't know about it
                    updated_status = TaskStatus.FAILED.value
                    error_message = "Task lost in Celery worker"
                    needs_update = True
                    logger.error(f"Task {task_id} lost in Celery, marking as failed")
                    
            elif celery_result.state == 'RETRY':
                # Task is retrying
                if task.status != TaskStatus.PROCESSING.value:
                    updated_status = TaskStatus.PROCESSING.value
                    needs_update = True
                    
            elif celery_result.state == 'REVOKED':
                # Task was cancelled
                if task.status != TaskStatus.CANCELLED.value:
                    updated_status = TaskStatus.CANCELLED.value
                    needs_update = True
                    
        except Exception as e:
            logger.error(f"Error checking Celery status for task {task_id}: {e}")

        
        # Update database if needed
        if needs_update:
            try:
                task.status = updated_status
                if error_message and error_message != task.error_message:
                    task.error_message = error_message
                task.updated_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(f"Synchronized task {task_id} status to {updated_status}")
            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to sync task status for {task_id}: {e}")
        
        return task.to_dict()
    
    @staticmethod
    async def cancel_task(db: AsyncSession, task_id: str) -> Dict[str, Any]:
        """Cancel task"""
        result = await db.execute(
            select(TranslationTask).filter(TranslationTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status != TaskStatus.PROCESSING.value:
            raise HTTPException(status_code=400, detail="Task not in processing state")

        task.status = TaskStatus.CANCELLED.value
        await db.commit()

        # Cancel celery task
        try:
            celery_app.control.revoke(task_id, terminate=True)
        except Exception as e:
            logger.error(f"Failed to cancel celery task {task_id}: {e}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to cancel task")

        return {"message": "Task cancelled successfully"}