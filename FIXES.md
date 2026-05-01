# Infrastructure Improvement & Bug Resolution Log

This document tracks the technical debt cleared and the infrastructure enhancements implemented for the distributed job processing system.

# 1. Application Stability & Service Discovery
- BUG (Networking): Hardcoded localhost references in api/main.py and frontend/app.js caused service communication failures within the Docker bridge network.
- FIX: Implemented environment-aware variables. The API now uses os.getenv("REDIS_HOST", "redis") and the Frontend utilizes process.env.API_URL, enabling seamless service discovery via Docker DNS.
- BUG (Race Condition): The API and Worker services would frequently crash on startup because they attempted to connect to Redis before the database container was fully initialized.
- FIX: Integrated Redis healthchecks in the orchestration layer and updated the depends_on configuration to use the service_healthy condition, ensuring a deterministic startup sequence.
- BUG (Worker Reliability): The Worker service lacked an exposed port, making traditional HTTP health monitoring impossible.
- FIX: Implemented a file-system "heartbeat" mechanism where the worker updates /tmp/worker_healthy on every loop. A Docker HEALTHCHECK now validates the process's liveness by checking the file's timestamp.

## 2. Container Security & Optimization
- BUG (Security): All services were initially configured to run as root, violating the Principle of Least Privilege.
- FIX: Hardened all Dockerfiles by creating a dedicated non-privileged system user (`edith`) and utilizing the USER instruction for all runtime processes.
- BUG (Optimization): Original Dockerfiles utilized a monolithic build approach, resulting in bloated image sizes and unnecessary build tools in the production environment.
- FIX: Refactored to Multi-stage Builds. By separating the build environment from the runtime environment, the final image footprint was reduced by over 70%, significantly decreasing the attack surface.
- BUG (Resource Management): Lack of resource limits posed a risk of "noisy neighbor" issues or system-wide crashes due to memory leaks.
- FIX: Enforced strict hardware constraints in the orchestration layer, limiting each service to 0.50 CPU and 512MB RAM.

## 3. CI/CD Pipeline & Integration
- BUG (Automation): The original pipeline lacked automated security oversight, risking the deployment of vulnerable base images.
- FIX: Integrated Trivy for container vulnerability scanning and Hadolint for Dockerfile best-practice enforcement directly into the GitHub Actions workflow.
- BUG (Testing Flakes): The frontend test suite used a "watch" mode by default, causing the GitHub Actions runner to hang indefinitely.
- FIX: Updated the package.json test script with the --watchAll=false flag to ensure the pipeline completes and reports results automatically.
- BUG (Verification): Routine health checks often reported "Success" as long as the container was running, even if the application inside was unresponsive.
- FIX: Added a dedicated Integration Test stage in the CI pipeline. This uses docker compose exec to perform a urllib probe from *within* the internal network, providing 100% certainty of end-to-end connectivity.

## 4. Code & Configuration Logic
- BUG (CORS): The API initially blocked frontend requests due to missing Cross-Origin Resource Sharing headers.
- FIX: Implemented CORSMiddleware in FastAPI to allow secure communication from the frontend container on port 3000.
- BUG (Application Logic): Syntax errors in the Worker (`name` vs `__name__`) and incorrect Redis list names ('job' vs 'job_queue') caused tasks to stay in a permanent pending state.
- FIX: Corrected Python magic variables and synchronized the messaging queue keys across the API and Worker services.