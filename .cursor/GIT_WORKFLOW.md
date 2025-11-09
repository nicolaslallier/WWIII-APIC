# Git Workflow Quick Reference

## Using Makefile Commands

### Commit
```bash
# Generic commit
make git-commit MSG="your commit message"

# Feature commit
make git-commit-feat MSG="add user authentication"

# Fix commit
make git-commit-fix MSG="fix login bug"

# Refactor commit
make git-commit-refactor MSG="refactor auth service"
```

### Push
```bash
# Push current branch
make git-push

# Push and set upstream
make git-push-upstream
```

### Pull Request
```bash
# Create PR with custom title/body
make git-pr-create TITLE="Add feature" BODY="Description here"

# Create PR from last commit message (auto)
make git-pr-create-auto
```

### Complete Workflow
```bash
# Commit, push, and create PR in one command
make git-commit-push-pr MSG="feat: add user authentication"
```

## Using Shell Script

```bash
# Commit
./scripts/git-helper.sh commit feat "add user authentication"

# Push
./scripts/git-helper.sh push

# Create PR
./scripts/git-helper.sh pr "PR Title" "PR Body"

# Complete workflow
./scripts/git-helper.sh commit_push_pr feat "add user authentication"
```

## Using Cursor Commands

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Type command name (e.g., `git.commit.feat`)
3. Follow prompts

Available Cursor commands:
- `git.commit` - Commit with custom message
- `git.commit.feat` - Commit feature
- `git.commit.fix` - Commit fix
- `git.commit.refactor` - Commit refactor
- `git.push.current` - Push current branch
- `git.pr.create` - Create PR
- `git.commit.push.pr` - Complete workflow

## Conventional Commits Format

All commits follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks
- `docs:` - Documentation changes

Example: `feat: add user authentication endpoint`

