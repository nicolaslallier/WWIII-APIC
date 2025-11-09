#!/bin/bash
# Git workflow helper scripts
# These can be used as standalone scripts or referenced by Cursor commands

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to commit with Conventional Commits format
commit() {
    local type=$1
    shift
    local message="$*"
    
    if [ -z "$message" ]; then
        echo "Usage: commit <type> <message>"
        echo "Types: feat, fix, refactor, test, chore, docs"
        exit 1
    fi
    
    git add -A
    git commit -m "${type}: ${message}"
    echo -e "${GREEN}✓ Committed: ${type}: ${message}${NC}"
}

# Function to push current branch
push_current() {
    local branch=$(git branch --show-current)
    git push -u origin "$branch"
    echo -e "${GREEN}✓ Pushed ${branch} to origin${NC}"
}

# Function to create PR
create_pr() {
    local title="${1:-$(git log -1 --pretty=%B)}"
    local body="${2:-## Changes\n\n- \n\n## Testing\n\n- [ ] Tests pass\n- [ ] Quality gates pass}"
    local base="${3:-main}"
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠ GitHub CLI (gh) not installed. Install it first.${NC}"
        exit 1
    fi
    
    gh pr create --title "$title" --body "$body" --base "$base"
    echo -e "${GREEN}✓ PR created${NC}"
}

# Function for complete workflow
commit_push_pr() {
    local type=$1
    shift
    local message="$*"
    
    if [ -z "$message" ]; then
        echo "Usage: commit_push_pr <type> <message>"
        exit 1
    fi
    
    commit "$type" "$message"
    push_current
    create_pr "$(git log -1 --pretty=%B)"
}

# Main command dispatcher
case "${1:-}" in
    commit)
        shift
        commit "$@"
        ;;
    push)
        push_current
        ;;
    pr)
        shift
        create_pr "$@"
        ;;
    commit_push_pr)
        shift
        commit_push_pr "$@"
        ;;
    *)
        echo "Usage: $0 {commit|push|pr|commit_push_pr}"
        echo ""
        echo "Examples:"
        echo "  $0 commit feat 'add user authentication'"
        echo "  $0 push"
        echo "  $0 pr 'PR Title' 'PR Body'"
        echo "  $0 commit_push_pr feat 'add user authentication'"
        exit 1
        ;;
esac

