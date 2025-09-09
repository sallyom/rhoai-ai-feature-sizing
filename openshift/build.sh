#!/bin/bash

# Build Script for RHOAI AI Feature Sizing Platform
# Usage: ./build.sh [REGISTRY_URL] [IMAGE_TAG]
# Alternative: IMAGE_FULL_NAME=quay.io/user/image:tag ./build.sh
# Platform: PLATFORM=linux/amd64 ./build.sh (for x86) or PLATFORM=linux/arm64 ./build.sh (for ARM)

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
DEFAULT_PLATFORM="linux/amd64"  # Default to x86 for OpenShift compatibility

# Parse arguments - allow full image name override
if [ -n "$IMAGE_FULL_NAME" ]; then
    # Use provided full image name
    echo "Using provided IMAGE_FULL_NAME: $IMAGE_FULL_NAME"
else
    # Build from components
    REGISTRY_URL=${1:-$DEFAULT_REGISTRY}
    IMAGE_TAG=${2:-$DEFAULT_TAG}
    IMAGE_FULL_NAME="${REGISTRY_URL}/${APP_NAME}:${IMAGE_TAG}"
fi

# Set platform
PLATFORM=${PLATFORM:-$DEFAULT_PLATFORM}

echo -e "${BLUE}🔨 RHOAI AI Feature Sizing - Container Build${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Registry: ${GREEN}${REGISTRY_URL}${NC}"
echo -e "Image: ${GREEN}${IMAGE_FULL_NAME}${NC}"
echo -e "Platform: ${GREEN}${PLATFORM}${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites and detect container runtime
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
CONTAINER_RUNTIME=""
if command_exists podman; then
    CONTAINER_RUNTIME="podman"
    echo -e "${GREEN}✅ Found Podman${NC}"
elif command_exists docker; then
    CONTAINER_RUNTIME="docker"
    echo -e "${GREEN}✅ Found Docker${NC}"
else
    echo -e "${RED}❌ Neither Docker nor Podman found. Please install one of them first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed (using ${CONTAINER_RUNTIME})${NC}"
echo ""

# Build container image
echo -e "${YELLOW}🔨 Building container image for ${PLATFORM}...${NC}"
if [ "$CONTAINER_RUNTIME" = "docker" ]; then
    # Use buildx for better cross-platform support
    docker buildx build --platform="${PLATFORM}" -t "${IMAGE_FULL_NAME}" --push .
else
    # Fallback for podman
    ${CONTAINER_RUNTIME} build --platform="${PLATFORM}" -t "${IMAGE_FULL_NAME}" .
fi

if [ "$CONTAINER_RUNTIME" != "docker" ]; then
    echo -e "${YELLOW}📤 Pushing container image to registry...${NC}"
    ${CONTAINER_RUNTIME} push "${IMAGE_FULL_NAME}"
else
    echo -e "${GREEN}✅ Image built and pushed via buildx${NC}"
fi
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
