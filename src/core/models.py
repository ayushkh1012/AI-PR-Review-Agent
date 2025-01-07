from typing import List, Dict, Optional, Any
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CodeIssue(BaseModel):
    description: str
    line: Optional[int] = None
    suggestion: Optional[str] = None
    severity: Optional[str] = "medium"

class FileAnalysis(BaseModel):
    path: str
    issues: List[CodeIssue]
    suggestions: List[str]
    complexity_score: int

class PRAnalysisRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    pr_number: int = Field(..., description="Pull request number")
    github_token: str = Field(..., description="GitHub personal access token")

    model_config = {
        "json_schema_extra": {
            "example": {
                "repo_url": "https://github.com/username/repository",
                "pr_number": 1,
                "github_token": "ghp_xxxxxxxxxxxxxxxxxxxx"
            }
        }
    }

class AnalysisResponse(BaseModel):
    task_id: str
    status: TaskStatus
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
