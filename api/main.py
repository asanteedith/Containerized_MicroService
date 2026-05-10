import os
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/jobs")
async def create_job():
    job_id = str(uuid.uuid4())
    r.hset(f"job:{job_id}", "status", "pending")
    r.lpush("job_queue", job_id)
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
async def get_status(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        return {"status": "not_found"}
    return {"status": status}
