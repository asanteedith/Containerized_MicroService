# FIXES.md — Bug Resolution Log

A complete record of every bug found and fixed in the starter repository. Each entry documents the file, the problem, and the exact fix applied.

---

## 1. Application Logic & Service Discovery

**Bug — Hardcoded localhost in API**
- File: `api/main.py`, line 8
- Problem: Redis connection used `localhost` which resolves to the container itself, not the Redis service.
- Fix: Changed to `os.getenv("REDIS_HOST", "redis")` to use Docker DNS for service discovery.

**Bug — Hardcoded localhost in Frontend**
- File: `frontend/app.js`, line 6
- Problem: API URL was hardcoded as `localhost:8000`, breaking container-to-container communication.
- Fix: Changed to `process.env.API_URL || "http://api:8000"` to use the Docker service name.

**Bug — Wrong Redis queue name in Worker**
- File: `worker/worker.py`
- Problem: Worker was polling a list called `job` while the API was pushing to `job_queue`, leaving all jobs permanently stuck in `pending` state.
- Fix: Updated `r.blpop` to use `job_queue` to match the API.

**Bug — Syntax error in Worker entry point**
- File: `worker/worker.py`
- Problem: Used `name` instead of the Python magic variable `__name__`, so the worker never started its main loop.
- Fix: Corrected to `if __name__ == "__main__":`.

**Bug — Redis returning byte strings**
- File: `api/main.py`
- Problem: Redis responses were raw bytes, causing formatting errors when building API responses.
- Fix: Added `decode_responses=True` to the Redis connection to get UTF-8 strings automatically.

**Bug — Missing CORS middleware**
- File: `api/main.py`
- Problem: Browser blocked frontend requests to the API due to missing Cross-Origin Resource Sharing headers.
- Fix: Added `CORSMiddleware` from FastAPI to allow requests from the frontend container on port 3000.

**Bug — Job ID key mismatch in Frontend**
- File: `frontend/views/index.html`
- Problem: Dashboard displayed `undefined` for the job ID because it was reading the wrong key from the API response.
- Fix: Updated key mapping to `data.job_id` to match the FastAPI response schema.

**Bug — JavaScript crash on failed API request**
- File: `frontend/views/index.html`
- Problem: `substring` error thrown when the API request failed and returned null.
- Fix: Added null checks and optional chaining to handle failed requests gracefully.

---

## 2. Container Security & Optimization

**Bug — All services running as root**
- File: All Dockerfiles
- Problem: Containers ran as root by default, violating the Principle of Least Privilege and creating a significant security risk.
- Fix: Created a dedicated non-privileged user (`edith`) in all Dockerfiles and switched to that user before the CMD instruction.

**Bug — Monolithic single-stage Docker builds**
- File: All Dockerfiles
- Problem: Build tools and dev dependencies were included in production images, increasing image size and attack surface.
- Fix: Refactored all Dockerfiles to use multi-stage builds — dependencies installed in a builder stage, only the compiled artifacts copied to the slim runtime stage. Image size reduced by over 70%.

**Bug — No resource limits**
- File: `docker-compose.yml`
- Problem: No CPU or memory constraints meant a misbehaving service could starve the entire host.
- Fix: Added `deploy.resources.limits` to every service — 0.50 CPU and 512MB RAM for api, frontend and worker; 0.25 CPU and 256MB RAM for redis.

**Bug — Redis exposed on host machine**
- File: `docker-compose.yml`
- Problem: Redis port was mapped to the host, making it accessible from outside the container network.
- Fix: Removed the host port mapping and used `expose` instead — Redis is only reachable internally.

---

## 3. Service Startup & Reliability

**Bug — Race condition on startup**
- File: `docker-compose.yml`
- Problem: API and Worker started immediately and crashed because they tried to connect to Redis before it was ready.
- Fix: Added a Redis `healthcheck` and changed `depends_on` to use `condition: service_healthy` — services only start after Redis confirms it is ready.

**Bug — Worker had no health check**
- File: `worker/Dockerfile`
- Problem: Docker had no way to detect if the worker process was alive but stuck.
- Fix: Implemented a filesystem heartbeat — the worker writes the current timestamp to `/tmp/worker_healthy` on every loop iteration. The `HEALTHCHECK` instruction validates liveness by checking that file exists.

**Bug — Missing dependencies in requirements files**
- File: `api/requirements.txt`, `worker/requirements.txt`
- Problem: `ModuleNotFoundError` on container startup because packages were imported but not listed.
- Fix: Added all missing packages — `fastapi`, `uvicorn`, `redis`, `pytest`, `pytest-cov`, `flake8`, `httpx`.

---

## 4. CI/CD Pipeline

**Bug — No linting stage**
- File: `.github/workflows/ci.yml`
- Problem: Code style issues and Dockerfile violations were never caught automatically.
- Fix: Added a dedicated `lint` stage running `flake8` for Python, `eslint` for JavaScript, and `hadolint` for all Dockerfiles.

**Bug — No separate build stage**
- File: `.github/workflows/ci.yml`
- Problem: Images were never built or tagged in the pipeline — the build stage was missing entirely.
- Fix: Added a `build` stage that starts a local Docker registry as a service container, builds all 3 images, tags each with the git SHA and `latest`, and pushes to the registry. Images saved as pipeline artifacts.

**Bug — No security scanning**
- File: `.github/workflows/ci.yml`
- Problem: Vulnerable base images could be deployed without any automated detection.
- Fix: Added a `security` stage using Trivy to scan all 3 images and upload SARIF reports as artifacts.

**Bug — Frontend test suite hung in watch mode**
- File: `frontend/package.json`
- Problem: The test script ran Jest in watch mode by default, causing the GitHub Actions runner to hang indefinitely and never complete.
- Fix: Added `--watchAll=false` flag to the test script so it runs once and exits.

**Bug — No integration test stage**
- File: `.github/workflows/ci.yml`
- Problem: The pipeline had no end-to-end validation — a broken stack could pass all unit tests and still deploy broken.
- Fix: Added an `integration-test` stage that starts the full stack, submits a real job through the API, and polls until it reaches `completed` status. Tears down cleanly on success or failure.

**Bug — No deploy stage**
- File: `.github/workflows/ci.yml`
- Problem: Deployment was entirely manual with no automation or safety checks.
- Fix: Added a `deploy` stage using `appleboy/ssh-action` that performs a rolling update — deploys the new API container first, waits up to 60 seconds for it to pass its health check, then deploys the worker and frontend. Aborts and leaves the old container running if the health check fails.

---

## 5. Code Quality

**Bug — PEP 8 violations throughout Python files**
- File: `api/main.py`, `worker/worker.py`
- Problem: Trailing whitespace, incorrect indentation, missing blank lines between functions, and module-level imports not at top of file caused flake8 to fail.
- Fix: Reformatted both files to comply with PEP 8 — moved all imports to the top, added required blank lines, removed trailing whitespace, fixed indentation to multiples of 4.

**Bug — CRLF line endings on Windows**
- File: `api/main.py`, `worker/worker.py`
- Problem: Files edited on Windows had CRLF line endings which caused flake8 to report phantom whitespace errors on Linux runners.
- Fix: Configured git with `core.autocrlf false` and converted files to LF endings.
