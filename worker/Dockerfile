FROM python:3.9-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN useradd -m edith
COPY --from=builder /root/.local /home/edith/.local
COPY . .

# Fix permissions as ROOT before switching
RUN chown -R edith:edith /home/edith /app
USER edith
ENV PATH=/home/edith/.local/bin:$PATH

CMD ["python", "-u", "worker.py"]