from fastapi import FastAPI
from celery import Celery
from .api.routes import router as api_router
from .core.config import Settings

# Load settings
settings = Settings()

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Initialize Celery
celery_app = Celery(
    "pr_reviewer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)
celery_app.config_from_object('src.core.celeryconfig')

# Add API routes
app.include_router(
    api_router,
    prefix=settings.API_V1_STR
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}