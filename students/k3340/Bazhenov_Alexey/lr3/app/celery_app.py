from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)
