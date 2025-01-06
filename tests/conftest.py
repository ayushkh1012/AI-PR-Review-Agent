import pytest
from fastapi.testclient import TestClient
from redis import Redis
import asyncio
from typing import Generator
from src.main import app
from src.core.config import Settings
from src.utils.check_llm import check_llm

# Load settings
settings = Settings()

# Test client fixture
@pytest.fixture
def client() -> Generator:
    with TestClient(app) as test_client:
        yield test_client

# Redis fixture
@pytest.fixture
def redis_client() -> Generator:
    redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    try:
        yield redis
    finally:
        redis.close()

# LLM fixture
@pytest.fixture
async def llm_client():
    is_working = await check_llm()
    if not is_working:
        pytest.skip("LLM is not available")
    return is_working

# Mock PR data fixture
@pytest.fixture
def sample_pr_data():
    return {
        "repo_url": "https://github.com/test/repo",
        "pr_number": 1,
        "github_token": "test_token"
    }

# Mock PR diff fixture
@pytest.fixture
def sample_pr_diff():
    return """diff --git a/main.py b/main.py
index 83db48f..bf9f3ad 100644
--- a/main.py
+++ b/main.py
@@ -13,6 +13,7 @@ def process_data(data):
     # Process the data
     result = None
    if data is not None:
+        print(data)
        result = data * 2
    return result""" 