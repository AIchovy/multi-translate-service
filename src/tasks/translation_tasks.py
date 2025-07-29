"""
Speech-to-Text (STT) tasks for Celery
"""

import whisper
from typing import Dict, Any
from datetime import datetime, timezone
from celery import shared_task

from src.services.llm_translate_service import LLMTranslateService
from src.services.similarity_service import SimilarityService
from src.configs.config import settings
from src.utils.logger import get_logger
from src.models.base import get_sync_db
from src.models.translation_model import TranslationTask, TaskStatus
from src.utils.file import cleanup_temp_file, download_url_to_temp_file

logger = get_logger(__name__)


@shared_task(bind=True, name='src.tasks.translation_tasks.stt_task', queue='translation_task_queue',
             autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def stt_task(self, task_id: str) -> Dict[str, Any]:
    logger.info(f"Processing STT task for {task_id}")

    db = get_sync_db()
    try:
        # Get task from database
        task = db.query(TranslationTask).filter(
            TranslationTask.task_id == task_id).first()
        if not task:
            error_msg = f"Task not found: {task_id}"
            logger.error(error_msg)
            return {"error": error_msg}

        # Update task status to processing
        task.status = TaskStatus.PROCESSING.value
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Updated task {task_id} status to PROCESSING")

        # Load Whisper model and process audio
        temp_file_path = download_url_to_temp_file(task.audio_url)

        model = whisper.load_model(settings.whisper_model)
        result = model.transcribe(temp_file_path)

        # Prepare STT result
        stt_result = {
            "text": result["text"],
            "language": result["language"],
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        # Check if the STT result is accurate
        original_text = task.original_text
        if original_text:
            # Calculate the similarity between the original text and the STT result
            similarity = SimilarityService.calculate_similarity(
                original_text, result["text"])
            if similarity < 0.8:
                error_msg = f"STT result is not accurate, similarity: {similarity}"
                task.status = TaskStatus.FAILED.value
                task.error_message = error_msg
                task.updated_at = datetime.now(timezone.utc)
                db.commit()
                logger.error(f"STT task failed for {task_id}: {result['text']}")
                return {"error": error_msg}

        # Translate the text
        service = LLMTranslateService()
        multi_translate_result = service.translate(
            result["text"], task.target_languages)

        # Update task with STT results
        task.stt_result = stt_result
        task.translation_results = multi_translate_result
        task.status = TaskStatus.COMPLETED.value
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"STT task completed for {task_id}: {result['text']}")
        logger.info(f"Detected language: {result['language']}")

        return {
            "message": "STT task processed successfully",
            "task_id": task_id,
            "text": result["text"],
            "language": result["language"]
        }

    except Exception as e:
        db.rollback()
        error_msg = f"STT processing error for {task_id}: {str(e)}"
        logger.error(error_msg)

        # Update task status to failed
        try:
            task = db.query(TranslationTask).filter(
                TranslationTask.task_id == task_id).first()
            if task:
                task.status = TaskStatus.FAILED.value
                task.error_message = error_msg
                task.updated_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as db_error:
            logger.error(
                f"Failed to update error status for task {task_id}: {str(db_error)}")

        # Re-raise for Celery retry mechanism
        raise

    finally:
        db.close()
        cleanup_temp_file(temp_file_path)
