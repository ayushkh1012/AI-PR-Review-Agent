from enum import Enum
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PRAnalysisRequest(BaseModel):
    repo_url: HttpUrl
    pr_number: int
    github_token: str

class CodeIssue(BaseModel):
    type: str
    line: int
    description: str
    suggestion: str

class FileAnalysis(BaseModel):
    name: str
    issues: List[CodeIssue]

class AnalysisSummary(BaseModel):
    total_files: int
    total_issues: int
    critical_issues: int

class AnalysisResponse(BaseModel):
    task_id: str
    status: TaskStatus
    results: Optional[Dict] = None
