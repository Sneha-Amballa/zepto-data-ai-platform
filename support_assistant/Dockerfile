# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MOCK_LLM=1

# Set work directory
WORKDIR /app

# Install system build dependencies (e.g. gcc, g++, python3-dev for chromadb/hnswlib compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and documents
COPY . .

# Run database ingestion to pre-populate the persistent ChromaDB collection
RUN python ingest.py

# Expose FastAPI port
EXPOSE 7860

# Run uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
