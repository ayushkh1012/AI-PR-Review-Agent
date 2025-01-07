from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from ..core.models import PRAnalysisRequest, AnalysisResponse, TaskStatus
from ..core.github import GitHubClient
from ..core.config import Settings
from ..tasks.analysis import perform_analysis
from .dependencies import get_github_client
import redis
import json
import uuid
import logging
from typing import Dict

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Redis client
redis_client = redis.StrictRedis.from_url(
    Settings().REDIS_URL, 
    db=0, 
    decode_responses=True
)

@router.post("/analyze-pr", response_model=AnalysisResponse)
async def analyze_pr(
    request: PRAnalysisRequest,
    background_tasks: BackgroundTasks,
    github_client: GitHubClient = Depends(get_github_client)
) -> Dict:
    """
    Start a new PR analysis task
    """
    try:
        # Generate unique task ID
        task_id = f"task_{uuid.uuid4().hex}"
        
        # Fetch PR diff from GitHub
        diff = await github_client.get_pr_diff(
            request.repo_url,
            request.pr_number
        )
        
        if not diff:
            raise HTTPException(
                status_code=404,
                detail="PR not found or empty"
            )
        
        # Initialize task status in Redis
        redis_client.set(
            f"{task_id}:status",
            TaskStatus.PENDING.value
        )
        
        # Queue the analysis task
        background_tasks.add_task(
            perform_analysis,
            task_id=task_id,
            code=diff.encode()
        )
        
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus.PENDING
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting analysis: {str(e)}"
        )

@router.get("/status/{task_id}", response_model=AnalysisResponse)
async def get_status(task_id: str) -> Dict:
    """
    Check the status of an analysis task
    """
    try:
        # Get status from Redis
        status = redis_client.get(f"{task_id}:status")
        if not status:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        # Get error if exists
        error = redis_client.get(f"{task_id}:error")
        
        # Get results if completed
        results = None
        if status == TaskStatus.COMPLETED.value:
            results_str = redis_client.get(f"{task_id}:result")
            if results_str:
                results = json.loads(results_str)
        
        # Log for debugging
        logger.info(f"Task {task_id} status: {status}")
        if error:
            logger.error(f"Task {task_id} error: {error}")
        
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus(status),
            results=results,
            error=error
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking status: {str(e)}"
        )

@router.get("/results/{task_id}", response_model=AnalysisResponse)
async def get_results(task_id: str) -> Dict:
    """
    Get the results of a completed analysis task
    """
    try:
        # Get status from Redis
        status = redis_client.get(f"{task_id}:status")
        if not status:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        # If task is not completed, return status
        if status != TaskStatus.COMPLETED.value:
            error = redis_client.get(f"{task_id}:error")
            return AnalysisResponse(
                task_id=task_id,
                status=TaskStatus(status),
                error=error
            )
        
        # Get results from Redis
        results = redis_client.get(f"{task_id}:result")
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Results not found"
            )
        
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            results=json.loads(results)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching results: {str(e)}"
        )
