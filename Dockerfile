FROM python:3.9-slim

WORKDIR /app

ENV PYTHONPATH /app
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies explicitly mentioning uvicorn
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn fastapi

# Verify uvicorn is installed and accessible
RUN python -c "import uvicorn; print(f'uvicorn version: {uvicorn.__version__}')"

# Copy the entire project
COPY .. .

# Make sure scripts directory is executable
RUN chmod +x scripts/*.py 2>/dev/null || true

# Create necessary directories if they don't exist
RUN mkdir -p data/plots data/jobs

# Expose port for the API
EXPOSE 8000

# Command to run the application using python -m to ensure proper module resolution
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]