import os
import time
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "job_queue"


def process_tasks():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    print(f"Worker connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

    while True:
        try:
            with open('/tmp/worker_healthy', 'w') as f:
                f.write(str(time.time()))

            task = r.blpop(QUEUE_NAME, timeout=5)

            if task:
                job_id = task[1].decode('utf-8')
                print(f"Processing task: {job_id}")
                time.sleep(2)
                r.hset(f"job:{job_id}", "status", "completed")
                print("Task complete.")

        except redis.ConnectionError:
            print("Redis not available, retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    process_tasks()
