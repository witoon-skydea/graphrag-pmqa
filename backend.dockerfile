FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app /app
COPY data /data

# Create necessary directories
RUN mkdir -p /data/documents/raw
RUN mkdir -p /data/documents/หมวด_1
RUN mkdir -p /data/documents/หมวด_2
RUN mkdir -p /data/documents/หมวด_3
RUN mkdir -p /data/documents/หมวด_4
RUN mkdir -p /data/documents/หมวด_5
RUN mkdir -p /data/documents/หมวด_6
RUN mkdir -p /data/documents/หมวด_7
RUN mkdir -p /data/chroma_db
RUN mkdir -p /logs

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
