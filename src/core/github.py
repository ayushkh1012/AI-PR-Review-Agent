from typing import Optional
import httpx
from ..utils.helpers import parse_github_url
from .config import Settings

class GitHubClient:
    """GitHub API client for fetching PR information"""
    
    def __init__(self, token: str):
        """
        Initialize GitHub client.
        
        Args:
            token (str): GitHub API token
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_pr_diff(self, repo_url: str, pr_number: int) -> Optional[str]:
        """
        Fetch PR diff from GitHub.
        
        Args:
            repo_url (str): GitHub repository URL
            pr_number (int): Pull request number
            
        Returns:
            Optional[str]: PR diff content if successful
            
        Raises:
            ValueError: If PR not found
            Exception: For other API errors
        """
        try:
            # Extract owner and repo from URL
            owner, repo = parse_github_url(repo_url)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                    headers={**self.headers, "Accept": "application/vnd.github.v3.diff"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    raise ValueError("PR not found")
                else:
                    raise Exception(f"GitHub API error: {response.status_code}")
                    
        except httpx.TimeoutException:
            raise Exception("GitHub API timeout")
        except Exception as e:
            raise Exception(f"Error fetching PR diff: {str(e)}")

    async def get_pr_files(self, repo_url: str, pr_number: int) -> list:
        """
        Fetch list of files modified in PR.
        
        Args:
            repo_url (str): GitHub repository URL
            pr_number (int): Pull request number
            
        Returns:
            list: List of modified files
        """
        try:
            owner, repo = parse_github_url(repo_url)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files",
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise ValueError("PR not found")
                else:
                    raise Exception(f"GitHub API error: {response.status_code}")
                    
        except Exception as e:
            raise Exception(f"Error fetching PR files: {str(e)}")
