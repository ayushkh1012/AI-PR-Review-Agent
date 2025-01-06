import httpx
from typing import Optional
from .config import Settings

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.settings = Settings()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": self.settings.GITHUB_API_VERSION
        }

    async def get_pr_diff(self, repo_url: str, pr_number: int) -> Optional[str]:
        """Fetch PR diff from GitHub"""
        # Extract owner and repo from URL
        _, _, _, owner, repo = repo_url.rstrip('/').split('/')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers={**self.headers, "Accept": "application/vnd.github.v3.diff"}
            )
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                raise ValueError("PR not found")
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
