import pytest
from src.agents import CodeReviewAgent, SecurityAgent, StyleAgent
from langchain.llms import Ollama

@pytest.mark.asyncio
async def test_code_review_agent(llm_client, sample_pr_diff):
    """Test code review agent"""
    llm = Ollama(base_url="http://localhost:11434", model="llama2:3.2")
    agent = CodeReviewAgent(llm)
    result = await agent.analyze(sample_pr_diff)
    assert isinstance(result, dict)
    assert "issues" in result

@pytest.mark.asyncio
async def test_security_agent(llm_client, sample_pr_diff):
    """Test security agent"""
    llm = Ollama(base_url="http://localhost:11434", model="llama2:3.2")
    agent = SecurityAgent(llm)
    result = await agent.analyze(sample_pr_diff)
    assert isinstance(result, dict)
    assert "security_issues" in result

@pytest.mark.asyncio
async def test_style_agent(llm_client, sample_pr_diff):
    """Test style agent"""
    llm = Ollama(base_url="http://localhost:11434", model="llama2:3.2")
    agent = StyleAgent(llm)
    result = await agent.analyze(sample_pr_diff)
    assert isinstance(result, dict)
    assert "style_issues" in result 