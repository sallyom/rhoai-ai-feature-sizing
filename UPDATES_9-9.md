# RHOAI AI Feature Sizing - Updates 9/9

## Overview
Platform improvements including local embeddings, file upload functionality, container optimizations, and OpenShift deployment enhancements.

## Key Features Added

### 🚀 **Local Embeddings Support**
- Added `sentence-transformers` with `all-MiniLM-L6-v2` model for CPU-based embeddings
- No external API dependency for RAG index generation
- Configured via `EMBEDDING_PROVIDER=local` environment variable

### 📤 **File Upload API**
- New FastAPI service (`src/api_server.py`) for dynamic content uploads
- Real-time RAG indexing of uploaded files across all agent knowledge bases
- REST endpoints: `/api/upload`, `/api/uploads`, `/api/rag/status`
- Runs on port 8001 with CORS support

### 🔧 **Enhanced RAG System**
- Improved agent analysis with context retrieval (`get_rag_context()`)
- Runtime RAG index generation with local embeddings
- Better error handling and logging
- Support for uploaded file metadata and source tracking

### 🐳 **Container Improvements**
- Reduced build complexity and image layers
- Better dependency management with `uv sync --frozen`
- Node.js 18 integration for UI builds

### ⚙️ **Deployment Enhancements**
- **Startup Script**: New `startup.sh` orchestrates all services
- **Port Configuration**: Consistent port mapping (LlamaDeploy: 8000, Upload: 8001, UI: 3000)
- **Environment Variables**: `LLAMA_DEPLOY_PORT`, `EMBEDDING_PROVIDER` support
- **OpenShift Compatibility**: Improved permissions and volume mounts

### 🌐 **OpenShift Improvements**
- **Namespace Flexibility**: Dynamic namespace support via `NAMESPACE` env var
- **Updated Build Scripts**: Podman/Docker support with platform selection
- **Service Configuration**: Proper port mapping for all services
- **Route Fixes**: Corrected UI route configuration
- **Resource Scaling**: Increased memory/CPU limits for ML workloads (4Gi/1000m)

### 🔄 **GitHub Actions**
- Automated container builds and registry pushes
- Multi-branch support (main, working-openshift-two)
- Quay.io integration with secret management

## Configuration Changes

### Environment Variables
```bash
# Local embeddings (no API key needed)
EMBEDDING_PROVIDER=local

# LlamaDeploy port alignment
LLAMA_DEPLOY_PORT=8000

# Optional: OpenShift AI integration
LLM_PROVIDER=openshift_ai
OPENSHIFT_AI_API_KEY=<your-key>
OPENSHIFT_AI_BASE_URL=<your-endpoint>
```

### Port Mapping
- **4501**: LlamaDeploy internal (legacy compatibility)
- **8000**: LlamaDeploy external API
- **8001**: File Upload API
- **3000**: Standalone UI Server

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Server     │    │  LlamaDeploy    │    │  Upload API     │
│   Port 3000     │───▶│   Port 8000     │◀───│   Port 8001     │
│   (TypeScript)  │    │   (Workflows)   │    │   (File Mgmt)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Deployment Commands

### Quick Deploy
```bash
# Set your namespace
export NAMESPACE=your-namespace

# Deploy with your image
./openshift/deploy.sh quay.io/your-registry/rhoai-feature latest
```

### Manual Steps
```bash
# Update deployment configuration
oc apply -f openshift/deployment.yaml

# Restart with new environment variables
oc rollout restart deployment/rhoai-ai-feature-sizing -n $NAMESPACE
```

## What's Working Now
- ✅ Local embeddings (no OpenAI API key needed for indexing)
- ✅ Multi-service architecture with proper port mapping
- ✅ File upload and dynamic RAG indexing
- ✅ All 16 AI agents with enhanced context retrieval
- ✅ TypeScript UI compilation and standalone server
- ✅ OpenShift namespace flexibility
- ✅ Container build optimizations

## Next Steps
- Test UI route accessibility with corrected port configuration
- Validate agent workflows with uploaded content
- Consider microservices architecture for faster iteration cycles
- Add file type validation and size limits for production

