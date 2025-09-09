# OpenShift Deployment Changes

This document summarizes the changes made to adapt the RHOAI AI Feature Sizing platform for deployment on OpenShift.

## Summary

Successfully adapted the multi-agent RFE analysis system to run on OpenShift with:
- ✅ **OpenShift AI model endpoint integration** for LLM generation
- ✅ **Local lightweight embeddings** using sentence-transformers (all-MiniLM-L6-v2)
- ✅ **Cross-platform container builds** (Docker/Podman, ARM/x86)
- ✅ **OpenShift-compatible deployment** with proper permissions and storage

## Key Changes

### 1. Model Endpoint Configuration

**Files**: `src/settings.py`, `openshift/configmap.yaml`, `openshift/secret.yaml`

- **Added OpenShift AI provider** with support for OpenAI-compatible endpoints
- **Configured for your model endpoint** with API key and base URL
- **Local embeddings** to eliminate need for external embedding service

```yaml
# ConfigMap
LLM_PROVIDER: "openshift_ai"           # Your model endpoint
EMBEDDING_PROVIDER: "local"            # Local sentence-transformers

# Secret  
OPENSHIFT_AI_API_KEY: "your-api-key"
OPENSHIFT_AI_BASE_URL: "your-endpoint-url"
```

### 2. Local Embeddings Implementation

**Files**: `src/local_embeddings.py`, `pyproject.toml`

- **Created lightweight embedding class** using sentence-transformers
- **all-MiniLM-L6-v2 model** (~90MB, high quality)
- **Eliminated external embedding API calls**
- **Added sentence-transformers dependency**

### 3. Container Build Improvements  

**Files**: `openshift/build.sh`, `Dockerfile`

- **Cross-platform builds** - supports Docker/Podman automatically
- **ARM to x86 cross-compilation** for Mac → OpenShift deployment  
- **OpenShift permissions** - fixed file permissions for container security
- **Split RUN commands** to avoid QEMU segfaults during builds

```bash
# New capabilities
PLATFORM=linux/amd64 IMAGE_FULL_NAME=quay.io/user/image:tag ./build.sh
```

### 4. Deployment Script Enhancements

**Files**: `openshift/deploy.sh`

- **Flexible namespace support** via environment variable
- **Automatic manifest updates** for custom namespaces
- **Improved error handling** and status reporting

```bash
# Custom namespace deployment
NAMESPACE=sallyom-rhoai-feature ./openshift/deploy.sh
```

### 5. Application Startup Fix

**Files**: `deploy.py`

- **Fixed LlamaDeploy import errors** - original used non-existent API
- **Simplified container startup** - removed async complexity
- **Direct API server launch** using subprocess calls

### 6. Storage Configuration

**Files**: `openshift/pvc.yaml`

- **Updated storage class** from `standard-csi` to `ocs-external-storagecluster-ceph-rbd`
- **Fixed PVC binding issues** specific to your OpenShift cluster

## Architecture Overview

**Before**: Required 2 external endpoints (LLM + embeddings)
**After**: Only 1 external endpoint needed (your OpenShift AI model)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  LlamaDeploy    │───▶│ 16 AI Agents   │
│   (Web UI)      │    │   Orchestrator  │    │   (Parallel)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Local Embeddings│    │OpenShift AI LLM │
                       │  (in container) │    │ (your endpoint) │
                       └─────────────────┘    └─────────────────┘
```

## Benefits Achieved

1. **Simplified Infrastructure**: One model endpoint instead of two
2. **Faster Deployment**: Local embeddings, no external embedding API calls  
3. **Better Security**: All embedding processing happens in-cluster
4. **Cost Reduction**: No external embedding API costs
5. **Reduced Latency**: Local embeddings eliminate network calls
6. **Lighter Containers**: Optimized for OpenShift constraints

## Deployment Commands

```bash
# Build for OpenShift (x86)
IMAGE_FULL_NAME=quay.io/sallyom/rhoai-feature:latest ./openshift/build.sh

# Deploy to custom namespace  
NAMESPACE=sallyom-rhoai-feature ./openshift/deploy.sh

# Access UI
https://rhoai-ui-{namespace}.apps.{cluster}/deployments/rhoai-ai-feature-sizing/ui
```

## Next Steps for Production

1. **Frontend Separation**: Split into separate frontend/backend containers
2. **Resource Optimization**: Tune memory/CPU limits based on usage
3. **Horizontal Scaling**: Add replica scaling for high availability
4. **Monitoring**: Add prometheus metrics and health checks
5. **Security Hardening**: Review RBAC and network policies

## Files Changed

- `Dockerfile` - OpenShift permissions and build optimizations
- `deploy.py` - Fixed LlamaDeploy startup issues  
- `openshift/build.sh` - Cross-platform builds, flexible image naming
- `openshift/deploy.sh` - Namespace flexibility, manifest updates
- `openshift/*.yaml` - Updated for your namespace and storage class
- `src/settings.py` - Added OpenShift AI provider and local embeddings
- `src/local_embeddings.py` - **NEW** - Local embedding implementation
- `pyproject.toml` - Added sentence-transformers dependency

---

*Generated during OpenShift deployment collaboration - January 2025*