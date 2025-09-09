#!/bin/bash
set -e

# Ensure Node.js is in PATH
export PATH="/usr/bin:$PATH"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

echo "Generating RAG indices with local embeddings..."
EMBEDDING_PROVIDER=local PYTHONPATH=/app uv run python src/rag.py ingest

echo "Starting LlamaDeploy API server in background..."
uv run -m llama_deploy.apiserver &

echo "Starting Upload API server in background..."
uv run python src/api_server.py &

echo "Starting standalone UI server in background..."
cd ui && HOST=0.0.0.0 npm start &
cd /app

echo "Waiting for API servers to be ready..."
sleep 10

echo "Deploying workflows..."
uv run llamactl deploy deployment.yml

echo "API servers are running. Bringing to foreground..."
wait
