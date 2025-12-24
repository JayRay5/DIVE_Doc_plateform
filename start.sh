#!/bin/bash

echo "Starting the backend server (FastAPI)..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

sleep 5

echo "Starting the gradio interface..."
python app.py