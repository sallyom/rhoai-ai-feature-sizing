#!/bin/bash
set -e

# Ensure Node.js is in PATH
export PATH="/usr/bin:$PATH"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

echo "Checking RAG indices..."
if [ ! -d "/app/output/python-rag" ] || [ -z "$(ls -A /app/output/python-rag 2>/dev/null)" ]; then
    echo "Generating RAG indices with local embeddings..."
    EMBEDDING_PROVIDER=local PYTHONPATH=/app uv run python src/rag.py ingest
else
    echo "RAG indices already exist, skipping generation..."
fi

echo "Starting all services in parallel..."

# Start LlamaDeploy API server bound to all interfaces
uv run -m llama_deploy.apiserver --host 0.0.0.0 --port 4501 &
LLAMA_PID=$!

# Start UI server (now with built-in file upload)
cd ui && HOST=0.0.0.0 npm start &
UI_PID=$!
cd /app

echo "Waiting for services to initialize..."
sleep 15

echo "Deploying workflows..."
uv run llamactl deploy deployment.yml || echo "Workflow deployment failed, will retry..."

echo "API servers are running. Bringing to foreground..."
wait
