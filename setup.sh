#!/bin/bash

# Setup script for GraphRAG PMQA system

echo "====================="
echo "GraphRAG PMQA Setup"
echo "====================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/documents/raw
mkdir -p data/documents/หมวด_1
mkdir -p data/documents/หมวด_2
mkdir -p data/documents/หมวด_3
mkdir -p data/documents/หมวด_4
mkdir -p data/documents/หมวด_5
mkdir -p data/documents/หมวด_6
mkdir -p data/documents/หมวด_7
mkdir -p data/chroma_db
mkdir -p logs

# Check if Neo4j is available
echo "Checking Neo4j availability..."
if command -v docker >/dev/null 2>&1; then
    if ! docker ps | grep -q graphrag-neo4j; then
        echo "Starting Neo4j using Docker..."
        docker run --name graphrag-neo4j -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/password \
            -d neo4j:5.11.0
        # Wait for Neo4j to start
        echo "Waiting for Neo4j to start..."
        sleep 15
    else
        echo "Neo4j is already running in Docker."
    fi
else
    echo "Docker not available. Please make sure Neo4j is running at bolt://localhost:7687"
fi

# Check if Ollama is available
echo "Checking Ollama availability..."
if command -v ollama >/dev/null 2>&1; then
    echo "Ollama is installed. Pulling required models..."
    echo "This might take a while..."
    python scripts/pull_models.py
else
    echo "Ollama not found. Please install Ollama and run: python scripts/pull_models.py"
fi

# Initialize Neo4j database
echo "Initializing Neo4j database with PMQA structure..."
python scripts/init_db.py

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file to configure your environment."
fi

echo "====================="
echo "Setup complete!"
echo "====================="
echo "To run the backend: uvicorn app.main:app --reload"
echo "To run the frontend: streamlit run frontend/app.py"
echo "Or use Docker Compose: docker-compose up -d"
echo "====================="
