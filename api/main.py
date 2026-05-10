from fastapi import FastAPI
import os
import redis
import uuid

app=FastAPI()


r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"), 
    port=6379, 
    decode_responses=True 
)
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Endpoint to create a new job
@app.post("/jobs")
async def create_job():
    job_id = str(uuid.uuid4())
    # Create the job in Redis with a 'pending' status
    r.hset(f"job:{job_id}", "status", "pending")
    # Push the job ID to the queue for the worker to find
    r.lpush("job_queue", job_id)
    return {"job_id": job_id}


# Endpoint to check job status
@app.get("/jobs/{job_id}")
async def get_status(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        return {"status": "not_found"}
    return {"status": status}
