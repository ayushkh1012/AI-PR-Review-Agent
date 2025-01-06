import pytest
from src.workflows import PRReviewWorkflow
from langchain.llms import Ollama

@pytest.mark.asyncio
async def test_pr_review_workflow(llm_client, sample_pr_diff):
    """Test PR review workflow"""
    llm = Ollama(base_url="http://localhost:11434", model="llama2:3.2")
    workflow = PRReviewWorkflow(llm)
    result = await workflow.execute(sample_pr_diff)
    assert isinstance(result, dict)
    assert "summary" in result 