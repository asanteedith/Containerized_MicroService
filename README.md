# Containerized MicroService

A production-ready, containerized job processing system built with a Python FastAPI backend, Node.js frontend, Python background worker, and Redis message broker. The project demonstrates real-world DevOps practices including multi-stage Docker builds, automated CI/CD, container security hardening, and rolling deployments.

---

## Architecture

```
+----------------------------------------------------------+
|                    Docker Network (hng_network)          |
|                                                          |
|  User --HTTP:3000--> [ Frontend (Node.js) ]              |
|                              |                           |
|                        POST /jobs                        |
|                              |                           |
|                       [ API (FastAPI) ]                  |
|                              |                           |
|                        lpush job_queue                   |
|                              |                           |
|                         [ Redis ]                        |
|                              |                           |
|                        blpop job_queue                   |
|                              |                           |
|                       [ Worker (Python) ]                |
|                                                          |
+----------------------------------------------------------+
```

The system works as a distributed job processing pipeline:

1. A user submits a job through the frontend dashboard
2. The API creates a job entry in Redis and pushes the job ID to the queue
3. The worker picks up the job, processes it, and updates the status to completed
4. The frontend polls the API for the job status and displays the result

---

## Prerequisites

- Docker Engine 24+
- Docker Compose plugin
- Git

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/asanteedith/Containerized_MicroService.git
cd Containerized_MicroService

# 2. Set up environment
cp .env.example .env

# 3. Start the stack
docker compose up -d --build

# 4. Verify everything is running
docker compose ps
```

Access the services:
- Frontend: http://localhost:3000
- API Health: http://localhost:8000/health
- Submit a job: `curl -X POST http://localhost:8000/jobs`
- Check job status: `curl http://localhost:8000/jobs/<job_id>`

---

## Services

| Service | Image | Port | Description |
|---|---|---|---|
| frontend | node:18-alpine | 3000 | User dashboard for submitting and tracking jobs |
| api | python:3.11-slim | 8000 | FastAPI backend — creates jobs and serves status |
| worker | python:3.11-slim | internal | Background processor — picks up and completes jobs |
| redis | redis:alpine | internal | Message broker and job state store |

---

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push to main in strict order:

```
lint → test → build → security → integration-test → deploy
```

| Stage | Tool | What it does |
|---|---|---|
| lint | flake8, eslint, hadolint | Checks Python, JavaScript, and Dockerfile style |
| test | pytest + pytest-cov | Runs unit tests and uploads coverage report |
| build | Docker + local registry | Builds all 3 images tagged with git SHA and latest |
| security | Trivy | Scans all images for CRITICAL vulnerabilities |
| integration-test | docker compose | Starts full stack, submits a job, polls until completed |
| deploy | appleboy/ssh-action | Rolling update with health check gate before cutover |

A failure in any stage stops all subsequent stages from running.

---

## Security Hardening

- All services run as a dedicated non-root user (edith) following the Principle of Least Privilege
- Multi-stage Docker builds ensure build tools never reach production images
- No secrets committed — all configuration via environment variables
- Redis not exposed on the host machine — internal network only
- Resource limits enforced on every service

| Service | CPU Limit | Memory Limit |
|---|---|---|
| api | 0.50 | 512MB |
| frontend | 0.50 | 512MB |
| worker | 0.50 | 512MB |
| redis | 0.25 | 256MB |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| REDIS_HOST | redis | Redis hostname — Docker service name |
| REDIS_PORT | 6379 | Redis port |
| API_URL | http://api:8000 | Internal API URL used by the frontend |

---

## Project Structure

```
Containerized_MicroService/
├── api/                  # FastAPI backend
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/             # Node.js frontend
│   ├── Dockerfile
│   └── app.js
├── worker/               # Python background worker
│   ├── Dockerfile
│   └── worker.py
├── tests/                # Pytest unit tests
├── .github/
│   └── workflows/
│       └── ci.yml        # Full 6-stage CI/CD pipeline
├── docker-compose.yml
├── .env.example
├── FIXES.md
└── README.md
```

---

## Known Limitations

- Single VM deployment — not designed for multi-host or Kubernetes
- No authentication on API endpoints
- No log rotation on worker output
- Trivy findings are reported but not blocking — upgrade base images to resolve

---

See [FIXES.md](./FIXES.md) for a full log of every bug found and fixed in this project.
