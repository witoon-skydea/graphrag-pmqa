#!/bin/bash

# Start script for GraphRAG PMQA system

echo "====================="
echo "Starting GraphRAG PMQA System"
echo "====================="

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Start Backend
echo "Starting backend..."
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start Frontend
echo "Starting frontend..."
cd frontend
streamlit run app.py &
FRONTEND_PID=$!
cd ..

echo "====================="
echo "GraphRAG PMQA System started!"
echo "====================="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo "====================="
echo "Press Ctrl+C to stop all services"
echo "====================="

# Handle shutdown
function cleanup {
    echo "Stopping services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    echo "Services stopped."
    exit 0
}

trap cleanup SIGINT

# Keep script running
while true; do
    sleep 1
done
