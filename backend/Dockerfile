# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system deps required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ca-certificates \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and backend code
COPY requirements.txt /app/requirements.txt
COPY . /app

# Upgrade pip and install requirements
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Create folders for runtime (reports, chroma, models)
RUN mkdir -p /app/reports /app/chroma_db /app/models

# Expose port
EXPOSE 8000

# Default environment variables (can be overridden at runtime)
ENV CHROMA_PERSIST_DIR=/app/chroma_db
ENV MODEL_PATH=/app/models/carbon_model.pkl
ENV EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000

# If you want container logs more verbose, adjust uvicorn parameters
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
