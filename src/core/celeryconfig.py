from .config import Settings

settings = Settings()

# Redis connection URLs
broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
task_routes = {
    'src.tasks.analysis.*': {'queue': 'analysis'},
}
task_acks_late = True
task_reject_on_worker_lost = True 
