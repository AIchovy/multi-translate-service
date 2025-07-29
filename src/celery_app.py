"""
Celery application module for Multi Translate Service
"""

import os
from celery import Celery
from kombu import Queue

celery_app = Celery("celery_app")

class CeleryConfig:
    # Broker configuration (Redis)
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Task routes configuration
    task_routes = {
        'src.tasks.translation_tasks.stt_task': {
            'queue': 'translation_task_queue'
        }
    }
    
    # Queue configuration
    task_default_queue = 'default'
    task_queues = (
        Queue('default', routing_key='default'),
        Queue('translation_task_queue', routing_key='stt'),
    )

celery_app.config_from_object(CeleryConfig)

celery_app.autodiscover_tasks([
    'src.tasks.translation_tasks',
])