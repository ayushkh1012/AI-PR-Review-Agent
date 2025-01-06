from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PR Reviewer"
    
    # Redis Settings
    REDIS_URL: str
    
    # Ollama Settings
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "llama2"
    
    # GitHub Settings
    GITHUB_API_VERSION: str = "2022-11-28"
    
    class Config:
        env_file = ".env"