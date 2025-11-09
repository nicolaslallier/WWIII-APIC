#!/bin/bash
# Quality Gates Script
# Runs all quality checks independently

set -euo pipefail

echo "🔍 Running Quality Gates"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

FAILED=0

# Gate 1: Linting
echo ""
echo "Gate 1: Linting (ruff)..."
if make lint > /dev/null 2>&1; then
    print_status "Linting passed"
else
    print_error "Linting failed"
    FAILED=1
fi

# Gate 2: Format check
echo ""
echo "Gate 2: Format check (black)..."
if make format-check > /dev/null 2>&1; then
    print_status "Format check passed"
else
    print_error "Format check failed"
    FAILED=1
fi

# Gate 3: Type checking
echo ""
echo "Gate 3: Type checking (mypy)..."
if make type-check > /dev/null 2>&1; then
    print_status "Type checking passed"
else
    print_error "Type checking failed"
    FAILED=1
fi

# Gate 4: Tests
echo ""
echo "Gate 4: Running tests..."
if make test > /dev/null 2>&1; then
    print_status "Tests passed"
else
    print_error "Tests failed"
    FAILED=1
fi

# Gate 5: Coverage threshold
echo ""
echo "Gate 5: Coverage threshold..."
COVERAGE_OUTPUT=$(make coverage 2>&1)
if echo "$COVERAGE_OUTPUT" | grep -q "FAILED"; then
    print_error "Coverage below threshold"
    FAILED=1
else
    print_status "Coverage threshold met"
fi

# Gate 6: Docker build
echo ""
echo "Gate 6: Docker build..."
if make docker-build > /dev/null 2>&1; then
    print_status "Docker build passed"
else
    print_error "Docker build failed"
    FAILED=1
fi

echo ""
echo "========================"
if [ $FAILED -eq 0 ]; then
    print_status "All quality gates passed! 🎉"
    exit 0
else
    print_error "Some quality gates failed!"
    exit 1
fi

