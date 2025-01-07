from fastapi import Depends
from ..core.github import GitHubClient
from ..core.models import PRAnalysisRequest
from ..workflows.review_workflow import PRReviewWorkflow
from langchain_community.llms import Ollama
from ..core.config import Settings
import httpx
import logging

logger = logging.getLogger(__name__)

def get_github_client(request: PRAnalysisRequest) -> GitHubClient:
    """
    Create GitHub client with token from request
    """
    return GitHubClient(token=request.github_token)

def get_workflow() -> PRReviewWorkflow:
    """
    Create PR review workflow with Ollama LLM
    """
    settings = Settings()
    
    # Check available models
    try:
        response = httpx.get(f"{settings.OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            models = response.json()
            logger.info(f"Available models: {models}")
    except Exception as e:
        logger.error(f"Error checking models: {e}")
    
    llm = Ollama(
        base_url=settings.OLLAMA_URL,
        model="llama2:latest",  # Changed to match exact model name
        temperature=0.7,
        timeout=120
    )
    return PRReviewWorkflow(llm)
