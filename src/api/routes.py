from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from ..core.models import PRAnalysisRequest, AnalysisResponse, TaskStatus
from ..core.github import GitHubClient
from ..workflows.review_workflow import PRReviewWorkflow
from ..utils.helpers import generate_task_id
from ..tasks.analysis import perform_analysis
from .dependencies import get_github_client, get_workflow
import redis
import json

router = APIRouter()

redis_client = redis.StrictRedis.from_url(
    Settings().REDIS_URL, 
    db=0, 
    decode_responses=True
)

@router.post("/analyze-pr", response_model=AnalysisResponse)
async def analyze_pr(
    request: PRAnalysisRequest,
    background_tasks: BackgroundTasks,
    github_client: GitHubClient = Depends(get_github_client),
    workflow: PRReviewWorkflow = Depends(get_workflow)
):
    try:
        task_id = generate_task_id()
        diff = await github_client.get_pr_diff(
            request.repo_url,
            request.pr_number
        )
        
        redis_client.set(f"{task_id}:status", TaskStatus.PENDING.value)
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
        raise HTTPException(status_code=404, detail="PR not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=AnalysisResponse)
async def get_status(task_id: str):
    """Get the status of an analysis task"""
    try:
        status = redis_client.get(f"{task_id}:status")
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
            
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus(status)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid task status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{task_id}", response_model=AnalysisResponse)
async def get_results(task_id: str):
    """Get the results of an analysis task"""
    try:
        status = redis_client.get(f"{task_id}:status")
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
            
        if status != TaskStatus.COMPLETED.value:
            return AnalysisResponse(
                task_id=task_id,
                status=TaskStatus(status)
            )
            
        result = redis_client.get(f"{task_id}:result")
        if not result:
            raise HTTPException(status_code=404, detail="Results not found")
            
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            results=json.loads(result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid task data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
