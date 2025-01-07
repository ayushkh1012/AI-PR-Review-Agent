from langchain_community.llms import Ollama
from ..workflows.review_workflow import PRReviewWorkflow
from ..core.config import Settings
from typing import Dict
import os

class PRAnalyzer:
    def __init__(self):
        settings = Settings()
        self.llm = Ollama(
            base_url=settings.OLLAMA_URL,
            model="llama2:latest",
            temperature=0.1,
            top_p=0.9,
            num_ctx=4096,
            repeat_penalty=1.1
        )
        self.workflow = PRReviewWorkflow(self.llm)
    
    async def analyze_diff(self, diff: bytes) -> Dict:
        """
        Analyze a GitHub PR diff using the LangGraph workflow
        """
        # Convert bytes to string if needed
        diff_str = diff.decode('utf-8') if isinstance(diff, bytes) else diff
        
        # Execute the workflow
        result = await self.workflow.execute(diff_str)
        return result
