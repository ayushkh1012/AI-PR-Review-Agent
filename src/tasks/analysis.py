from celery import shared_task
from ..core.config import Settings
from .pr_analysis import PRAnalyzer
from ..core.models import TaskStatus
import redis
import json
import asyncio

redis_client = redis.StrictRedis.from_url(
    Settings().REDIS_URL, 
    db=0, 
    decode_responses=True
)

@shared_task(bind=True)
def perform_analysis(self, task_id: str, code: bytes):
    """
    Celery task to perform PR analysis
    """
    redis_client.set(f"{task_id}:status", TaskStatus.IN_PROGRESS.value)
    
    try:
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run analysis
        analyzer = PRAnalyzer()
        result = loop.run_until_complete(analyzer.analyze_diff(code))
        
        # Store results
        redis_client.set(f"{task_id}:result", json.dumps(result))
        redis_client.set(f"{task_id}:status", TaskStatus.COMPLETED.value)
        
        # Cleanup
        loop.close()
        
        return result
    except Exception as e:
        redis_client.set(f"{task_id}:status", TaskStatus.FAILED.value)
        redis_client.set(f"{task_id}:error", str(e))
        raise 