# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Python Backend
```bash
# Install dependencies
uv sync

# Generate vector indices for RAG
uv run generate

# Start LlamaDeploy API server
uv run -m llama_deploy.apiserver

# Deploy workflows
uv run llamactl deploy deployment.yml

# Type checking
uv run mypy src/

# Upload API server
uv run python src/api_server.py

# Run tests
uv run pytest
```

### TypeScript Frontend
```bash
# Install dependencies (in ui/ directory)
cd ui && npm install

# Development mode with hot reload
npm run dev

# Production build
npm run build
```

### Development Workflow
1. Generate RAG indices: `uv run generate`
2. Start LlamaDeploy API server: `uv run -m llama_deploy.apiserver` (runs on port 4501)
3. Start Upload API: `uv run python src/api_server.py` (runs on port 8001)
4. Start UI server: `cd ui && npm start` (serves on port 3000)
5. Deploy workflows: `uv run llamactl deploy deployment.yml`
6. Access UI at: http://localhost:3000 (includes chat + file upload)
7. Test file upload: Drag & drop documents to enhance agent knowledge

## Architecture Overview

This is a containerized multi-agent system for analyzing Request for Enhancement (RFE) descriptions. The system uses **LlamaDeploy** for workflow orchestration, **FastAPI** for file uploads, and **@llamaindex/server** for the TypeScript UI. All services run in a single container.

### Key Components

**LlamaDeploy Workflow Engine (Port 4501)**:
- Primary workflow: `src/rfe_builder_workflow.py` - Multi-agent RFE analysis
- Secondary workflow: `src/jira_rfe_to_architecture_workflow.py` - Architecture generation
- Agent coordination: `src/agents.py` - Manages 16 specialized AI agents
- RAG system: `src/rag.py` and `src/generate.py` - Vector index management
- Configuration: `src/settings.py` - LLM and embedding settings

**FastAPI Upload Service (Port 8001)**:
- File upload API: `src/api_server.py` - REST API for document uploads
- Upload processing: `src/upload_service.py` - Dynamic content processing
- RAG integration: Real-time index updates across all 16 agents
- Cache management: Automatic agent index refresh for immediate availability

**TypeScript UI Server (Port 3000)**:
- UI server: `ui/index.ts` - Standalone LlamaIndexServer
- File upload: `ui/components/file_upload.jsx` - Drag & drop interface with progress tracking
- Custom components: `ui/components/` - Workflow-specific React components
- Dual integration: Connects to LlamaDeploy workflows AND Upload API

**Multi-Agent System**:
- 16 specialized personas defined in `src/agents/*.yaml`
- Roles include Product Manager, Staff Engineer, UX Architect, Delivery Owner, etc.
- Agent-specific RAG knowledge bases with domain expertise
- Parallel analysis with coordinated synthesis

### Data Flow

1. **Preparation**: Run `uv run generate` to create vector indices from data sources
2. **Analysis**: User submits RFE via chat UI
3. **Multi-Agent Processing**: LlamaDeploy orchestrates all agents simultaneously
4. **RAG Retrieval**: Each agent queries domain-specific knowledge bases
5. **Synthesis**: Combine analyses into architecture diagrams, component teams, timelines
6. **Artifacts**: Generate structured deliverables (RFE documents, epics/stories, etc.)

### Configuration

- **LLM Models**: Configure in `src/settings.py` (OpenAI GPT-4 by default)
- **Agent Personas**: Add/modify YAML files in `src/agents/`
- **Knowledge Sources**: Place documentation in `data/` or configure GitHub repos in agent YAML
- **UI Customization**: Modify `ui/index.ts` for starter questions and component configuration
- **Environment**: Copy `env.template` to `src/.env` and configure API keys

### File Structure

```
/
├── src/                    # Python workflow engine
│   ├── agents/            # 16 agent YAML configurations
│   ├── *.py              # Workflows, RAG, and API components
│   └── settings.py        # LLM configuration
├── ui/                    # TypeScript UI server
│   ├── components/        # Custom React components
│   ├── layout/           # UI layout components
│   └── index.ts          # LlamaIndexServer configuration
├── data/                  # Local knowledge sources
├── openshift/             # OpenShift deployment manifests
├── deployment.yml         # LlamaDeploy workflow configuration
├── Dockerfile            # Container build definition
├── startup.sh            # Container startup script
└── pyproject.toml        # Python dependencies and scripts
```

### Development Notes

- OpenAI API keys required in `src/.env` (copy from `env.template`)
- Vector indices stored in `output/python-rag/{agent_name}/` after `uv run generate`
- Three services run in single container: LlamaDeploy (4501), Upload API (8001), UI (3000)
- UI server connects to both LlamaDeploy workflows AND Upload API
- All 16 agents use YAML configurations with JSON Schema validation
- **File Upload Feature**: Drag & drop interface automatically enhances all agent knowledge
- Uploaded files immediately available to all agents (automatic cache refresh)

### Container Deployment

```bash
# Build container with updated UI components
./openshift/build.sh

# Deploy to OpenShift
oc apply -f openshift/

# Check deployment
oc get pods,services,routes
```

### OpenShift Architecture

- Single container deployment with 3 exposed ports
- `rhoai-api` route → LlamaDeploy API (port 4501)
- `rhoai-ui` route → UI Server (port 3000) - **includes file upload interface**
- `rhoai-upload` route → Upload API (port 8001) - for direct API access
- Persistent storage for uploads and vector indices

### File Upload Integration

```bash
# Access complete interface (chat + upload)
https://rhoai-ui-{namespace}.apps.{cluster}/deployments/rhoai-ai-feature-sizing/ui

# Direct upload API access (if needed)
https://rhoai-upload-{namespace}.apps.{cluster}/api/upload
```

**Features**:
- **Drag & Drop Upload**: Intuitive file interface within chat UI
- **Universal Knowledge**: Files automatically indexed for all 16 agents
- **Real-time Feedback**: Upload progress and agent indexing status
- **File Management**: List and delete uploaded documents
- **Immediate Availability**: No restart required - agents see new content instantly