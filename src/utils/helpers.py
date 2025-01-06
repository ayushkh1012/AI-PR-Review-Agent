import uuid
from datetime import datetime

def generate_task_id() -> str:
    """Generate a unique task ID"""
    return f"{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

def parse_github_url(url: str) -> tuple:
    """Parse GitHub URL into owner and repo"""
    parts = url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    return parts[-2], parts[-1]
