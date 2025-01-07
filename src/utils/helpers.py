from typing import Tuple
import uuid
import re
from urllib.parse import urlparse

def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Parse GitHub URL to extract owner and repository name.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        Tuple[str, str]: Repository owner and name
        
    Raises:
        ValueError: If URL format is invalid
    """
    try:
        # Handle different GitHub URL formats
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        # Remove .git extension if present
        path = re.sub(r'\.git$', '', path)
        
        # Split path into parts
        parts = path.split('/')
        
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL format")
            
        owner = parts[0]
        repo = parts[1]
        
        return owner, repo
        
    except Exception as e:
        raise ValueError(f"Error parsing GitHub URL: {str(e)}")

def generate_task_id() -> str:
    """
    Generate a unique task ID.
    
    Returns:
        str: Unique task ID
    """
    return f"task_{uuid.uuid4().hex}"
