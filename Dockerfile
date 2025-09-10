FROM python:3.11-slim

WORKDIR /app

# Install all dependencies including Node.js
RUN apt-get update && apt-get install -y \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    pip install --no-cache-dir uv && \
    npm --version && node --version

# Copy dependency files and install Python dependencies
COPY pyproject.toml uv.lock* README.md ./
RUN uv sync --frozen

# Copy source and build UI
COPY src ./src
COPY ui ./ui
COPY data ./data
COPY deployment.yml ./

# Build UI dependencies and compile TypeScript
WORKDIR /app/ui
RUN npm cache clean --force && \
    npm install --no-optional && \
    chmod +x node_modules/.bin/* && \
    npx tsc
WORKDIR /app

# Create directories and set permissions for OpenShift
RUN mkdir -p output/python-rag uploads .config/llamactl && \
    chmod -R 777 uploads output .config && \
    chmod -R g+w /app && \
    chmod g+w /tmp

# Environment setup
ENV HOME=/app

EXPOSE 4501 3000

COPY startup.sh ./
RUN chmod +x startup.sh

CMD ["./startup.sh"]
