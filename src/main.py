from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from celery import Celery
from .api.routes import router as api_router
from .core.config import Settings
from .core.models import TaskStatus
import redis

# Load settings
settings = Settings()

# Redis connection
redis_client = redis.StrictRedis.from_url(
    settings.REDIS_URL, 
    db=0, 
    decode_responses=True
)

# Celery configuration
celery_app = Celery("pr_reviewer")
celery_app.config_from_object("src.core.celeryconfig")

# FastAPI app
app = FastAPI(title="PR Reviewer")

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}