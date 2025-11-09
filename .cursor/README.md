# Cursor Commands for Git Workflow

This directory contains Cursor IDE command shortcuts for common git operations.

## Available Commands

### Commit Commands
- **git.commit** - Stage all changes and commit with custom message
- **git.commit.feat** - Commit with `feat:` prefix (for new features)
- **git.commit.fix** - Commit with `fix:` prefix (for bug fixes)
- **git.commit.refactor** - Commit with `refactor:` prefix (for refactoring)

### Push Commands
- **git.push** - Push to specified remote and branch
- **git.push.current** - Push current branch to origin
- **git.push.set-upstream** - Push and set upstream tracking

### Pull Request Commands
- **git.pr.create** - Create PR using GitHub CLI with custom title/body
- **git.pr.create.auto** - Create PR using last commit message

### Combined Commands
- **git.commit.push** - Commit and push in one command
- **git.commit.push.pr** - Commit, push, and create PR (complete workflow)

### Utility Commands
- **git.status** - Show git status
- **git.branch.create** - Create and switch to new branch
- **git.log** - Show recent git log

## Usage

1. Open Command Palette (`Cmd+Shift+P` on Mac, `Ctrl+Shift+P` on Windows/Linux)
2. Type the command name (e.g., "git.commit.feat")
3. Follow prompts for inputs

## Prerequisites

- GitHub CLI (`gh`) must be installed for PR commands
- Git must be configured with remote repository

## Examples

### Quick Feature Commit and Push
```
1. Run: git.commit.feat
2. Enter: "add user authentication"
3. Run: git.push.current
```

### Complete Workflow (Commit + Push + PR)
```
1. Run: git.commit.push.pr
2. Enter commit message: "feat: add user authentication"
3. PR title will auto-populate from commit message
4. PR will be created automatically
```

