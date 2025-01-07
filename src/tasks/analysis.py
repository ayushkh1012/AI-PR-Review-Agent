from celery import shared_task
from ..core.config import Settings
from ..workflows.review_workflow import PRReviewWorkflow
from langchain_community.llms import Ollama
import redis
import json
import asyncio
import httpx
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def perform_analysis(self, task_id: str, code: bytes):
    """Execute PR analysis workflow"""
    settings = Settings()
    redis_client = redis.StrictRedis.from_url(settings.REDIS_URL)
    
    try:
        # Test Ollama connection first
        try:
            response = httpx.get(f"{settings.OLLAMA_URL}/api/tags")
            logger.info(f"Ollama tags response: {response.status_code}")
            if response.status_code != 200:
                raise Exception(f"Ollama server not responding: {response.status_code}")
            
            # Log available models
            models = response.json()
            logger.info(f"Available models: {models}")
            
        except Exception as e:
            error_msg = f"Ollama setup failed: {str(e)}"
            logger.error(error_msg)
            redis_client.set(f"{task_id}:error", error_msg)
            redis_client.set(f"{task_id}:status", "failed")
            raise Exception(error_msg)
        
        # Initialize LLM
        llm = Ollama(
            base_url=settings.OLLAMA_URL,
            model=settings.MODEL_NAME,
            temperature=0.7,
            timeout=120
        )
        
        # Test LLM
        try:
            test_response = llm.invoke("Test connection")
            logger.info(f"LLM test response: {test_response}")
        except Exception as e:
            error_msg = f"LLM test failed: {str(e)}"
            logger.error(error_msg)
            redis_client.set(f"{task_id}:error", error_msg)
            redis_client.set(f"{task_id}:status", "failed")
            raise Exception(error_msg)
        
        # Create workflow
        workflow = PRReviewWorkflow(llm)
        
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Execute workflow
        result = loop.run_until_complete(
            workflow.execute(code.decode())
        )
        
        # Store results
        redis_client.set(
            f"{task_id}:result",
            json.dumps(result)
        )
        redis_client.set(
            f"{task_id}:status",
            "completed"
        )
        
        loop.close()
        return result
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        logger.error(error_msg)
        redis_client.set(f"{task_id}:error", error_msg)
        redis_client.set(f"{task_id}:status", "failed")
        raise 