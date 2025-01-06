from fastapi import Depends, HTTPException
from ..core.github import GitHubClient
from ..workflows.review_workflow import PRReviewWorkflow
from langchain.llms import Ollama
from ..core.config import Settings

settings = Settings()

async def get_github_client(github_token: str):
    return GitHubClient(github_token)

async def get_llm():
    """Get configured Llama 3.2 instance"""
    return Ollama(
        base_url=settings.OLLAMA_URL,
        model="llama2:3.2",  # Specifically use Llama 3.2
        temperature=0.1,     # Lower temperature for more focused responses
        top_p=0.9,          # Nucleus sampling
        num_ctx=4096,       # Context window size
        repeat_penalty=1.1   # Reduce repetition
    )

async def get_workflow(llm=Depends(get_llm)):
    return PRReviewWorkflow(llm)
