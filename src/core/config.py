from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI PR Reviewer"
    API_V1_STR: str = "/api/v1"
    
    # GitHub settings
    GITHUB_TOKEN: str
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Ollama settings
    OLLAMA_URL: str = "http://127.0.0.1:11434"
    MODEL_NAME: str = "llama2"
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    class Config:
        env_file = ".env"