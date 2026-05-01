# Multi-Tier Microservices Infrastructure
This repository demonstrates a hardened, containerized DevOps architecture featuring a Python FastAPI backend, a Node.js/Express frontend, and a Redis-backed background worker. The project emphasizes automated CI/CD, container security, and resource orchestration.

# Architecture Overview

The system is orchestrated via Docker Compose into four primary services:
* API (Backend): A FastAPI service providing core logic and health monitoring.
* Frontend: A Node.js/Express application serving the user interface.
* Worker: A Python background processor handling asynchronous tasks.
* Redis: A high-performance message broker facilitating service communication.

# Core Application Logic
The application functions as a Distributed Job Processing System, designed to handle intensive tasks without compromising user experience:
* Task Ingestion: The Frontend provides a dashboard for users to submit data-intensive jobs to the API gateway.
* Asynchronous Queuing: The API offloads these jobs to Redis, ensuring the web interface remains responsive and "non-blocking."
* Distributed Execution: The Worker monitors the queue and processes jobs in the background, allowing the system to scale horizontally by adding more worker nodes as demand increases.

# Infrastructure & DevOps Features

* Multi-Stage Docker Builds: Optimized images to minimize attack surface and deployment footprint.
* Resource Constraints: Strict CPU (0.50) and Memory (512MB) limits applied to ensure system stability.
* Non-Privileged Execution: All services execute under a dedicated hng system user (UID 1000) for enhanced security.
* Automated CI/CD: A 3-stage GitHub Actions pipeline validating code quality, security, and integration.
* Container Health Probing: Integrated liveness checks ensure services are responsive before traffic routing.

# Deployment Guide

# Prerequisites
* Docker and Docker Compose
* Git

# Local Installation
1.  Clone the repository:
       git clone <https://github.com/asanteedith/hng14-stage2-devops>
    cd hng14-stage2-devops
    
2.  Environment Setup:
    Create a .env file based on the template:
       cp .env.example .env
    
3.  Launch the Stack:
       docker-compose up -d --build
    
4.  Verify Access:
    * Frontend: http://localhost:3000
    * API Health: http://localhost:8000/health

# CI/CD Pipeline Logic

The automated workflow (`ci.yml`) validates every push across three critical gates:
1.  Test & Lint: Executes Python unit tests (Pytest) and lints Dockerfiles (Hadolint).
2.  Security Scan: Performs container vulnerability assessments using Trivy.
3.  Integration Test: Verifies internal service connectivity using urllib probes within the Docker network.

# Documentation
A detailed log of technical debt cleared and specific infrastructure bugs resolved can be found in [FIXES.md](./FIXES.md).
