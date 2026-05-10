FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m edith
COPY --from=builder /root/.local /home/edith/.local
COPY . .
RUN chown -R edith:edith /home/edith /app
USER edith
ENV PATH=/home/edith/.local/bin:$PATH

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD test -f /tmp/worker_healthy || exit 1

CMD ["python", "-u", "worker.py"]
