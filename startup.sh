#!/bin/bash
set -e

echo "Starting LlamaDeploy services..."

# Start LlamaDeploy API server bound to all interfaces
echo "Starting LlamaDeploy control plane on 0.0.0.0:4501..."
uv run -m llama_deploy.apiserver --host 0.0.0.0 --port 4501 &
LLAMA_PID=$!

echo "Waiting for API server to be ready..."
sleep 10

echo "Deploying workflows (UI will start automatically)..."
printf "Y\nY\nY\nY\nY\n" | uv run llamactl deploy deployment.yml || echo "Workflow deployment failed, will retry..."

echo "LlamaDeploy is running with UI. Bringing to foreground..."
wait