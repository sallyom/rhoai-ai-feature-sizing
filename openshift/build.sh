#!/bin/bash

# Build Script for RHOAI AI Feature Sizing Platform
# Usage: 
#   ./build.sh [REGISTRY_URL] [IMAGE_TAG]
#   OR
#   IMAGE_FULL_NAME=registry/image:tag ./build.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="rhoai-ai-feature-sizing"
DEFAULT_REGISTRY="quay.io/gkrumbach07/llama-index-demo"
DEFAULT_TAG="latest"

# Parse arguments and environment variables
# Support both command line args and IMAGE_FULL_NAME environment variable
if [ -n "$IMAGE_FULL_NAME" ]; then
    # Use IMAGE_FULL_NAME if provided as environment variable
    echo -e "${BLUE}Using IMAGE_FULL_NAME from environment: ${IMAGE_FULL_NAME}${NC}"
else
    # Fall back to positional arguments
    REGISTRY_URL=${1:-$DEFAULT_REGISTRY}
    IMAGE_TAG=${2:-$DEFAULT_TAG}
    IMAGE_FULL_NAME="${REGISTRY_URL}/${APP_NAME}:${IMAGE_TAG}"
fi

echo -e "${BLUE}🔨 RHOAI AI Feature Sizing - Container Build${NC}"
echo -e "${BLUE}===========================================${NC}"
if [ -n "$REGISTRY_URL" ]; then
    echo -e "Registry: ${GREEN}${REGISTRY_URL}${NC}"
fi
echo -e "Image: ${GREEN}${IMAGE_FULL_NAME}${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect container runtime
detect_container_runtime() {
    if command_exists podman; then
        echo "podman"
    elif command_exists docker; then
        echo "docker"
    else
        echo ""
    fi
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
CONTAINER_RUNTIME=$(detect_container_runtime)

if [ -z "$CONTAINER_RUNTIME" ]; then
    echo -e "${RED}❌ Neither Docker nor Podman found. Please install one of them first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Using container runtime: ${CONTAINER_RUNTIME}${NC}"
echo ""

# Build container image
echo -e "${YELLOW}🔨 Building container image with ${CONTAINER_RUNTIME}...${NC}"
${CONTAINER_RUNTIME} build -t "${IMAGE_FULL_NAME}" .

echo -e "${YELLOW}📤 Pushing container image to registry...${NC}"
${CONTAINER_RUNTIME} push "${IMAGE_FULL_NAME}"
echo -e "${GREEN}✅ Image pushed successfully${NC}"
echo ""

echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo -e "${GREEN}==============================${NC}"
echo -e "Image: ${BLUE}${IMAGE_FULL_NAME}${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "1. Deploy the image:"
echo -e "   ${BLUE}./openshift/deploy.sh ${REGISTRY_URL} ${IMAGE_TAG}${NC}"
echo -e "2. Or deploy with defaults:"
echo -e "   ${BLUE}./openshift/deploy.sh${NC}"
echo ""
