#!/bin/bash
# CI Pipeline Script
# Runs quality gates and builds Docker image

set -euo pipefail

echo "🚀 Starting CI Pipeline for WWIII-APIC"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first."
    exit 1
fi

# Step 1: Linting
echo ""
echo "Step 1: Running linter (ruff)..."
if make lint; then
    print_status "Linting passed"
else
    print_error "Linting failed"
    exit 1
fi

# Step 2: Format check
echo ""
echo "Step 2: Checking code formatting..."
if make format-check; then
    print_status "Format check passed"
else
    print_error "Format check failed. Run 'make format' to fix."
    exit 1
fi

# Step 3: Type checking
echo ""
echo "Step 3: Running type checker (mypy)..."
if make type-check; then
    print_status "Type checking passed"
else
    print_error "Type checking failed"
    exit 1
fi

# Step 4: Run tests with coverage
echo ""
echo "Step 4: Running tests with coverage..."
if make coverage; then
    print_status "Tests passed"
else
    print_error "Tests failed"
    exit 1
fi

# Step 5: Check coverage threshold
echo ""
echo "Step 5: Checking coverage threshold..."
COVERAGE=$(make coverage 2>&1 | grep -oP 'TOTAL.*\K\d+%' | head -1 | sed 's/%//')
if [ -z "$COVERAGE" ]; then
    print_warning "Could not parse coverage. Continuing..."
else
    if [ "$COVERAGE" -ge 85 ]; then
        print_status "Coverage ${COVERAGE}% meets threshold (85%)"
    else
        print_error "Coverage ${COVERAGE}% is below threshold (85%)"
        exit 1
    fi
fi

# Step 6: Build Docker image
echo ""
echo "Step 6: Building Docker image..."
if make docker-build; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Step 7: Test Docker image healthcheck
echo ""
echo "Step 7: Testing Docker container healthcheck..."
CONTAINER_ID=$(docker run -d -p 8000:8000 --name ci-test-container wwiii-apic:latest 2>/dev/null || true)
sleep 5

if docker ps | grep -q ci-test-container; then
    if curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
        print_status "Healthcheck passed"
        docker stop ci-test-container > /dev/null 2>&1 || true
        docker rm ci-test-container > /dev/null 2>&1 || true
    else
        print_error "Healthcheck failed"
        docker stop ci-test-container > /dev/null 2>&1 || true
        docker rm ci-test-container > /dev/null 2>&1 || true
        exit 1
    fi
else
    print_error "Container failed to start"
    docker logs ci-test-container 2>/dev/null || true
    docker rm ci-test-container > /dev/null 2>&1 || true
    exit 1
fi

echo ""
echo "========================================"
print_status "CI Pipeline completed successfully! 🎉"

