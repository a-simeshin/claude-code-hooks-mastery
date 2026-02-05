#!/bin/bash
# Install Claude Code hooks for Java/React projects
# Usage: curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/install.sh | bash

set -e

REPO="a-simeshin/claude-code-hooks-mastery"
BRANCH="main"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing Claude Code hooks for Java/React...${NC}"

# Check if .claude already exists
if [ -d ".claude" ]; then
    echo -e "${YELLOW}Warning: .claude directory already exists${NC}"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    rm -rf .claude
fi

# Create temp directory
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Download and extract
echo "Downloading from github.com/${REPO}..."
curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz -C "$TMP_DIR"

# Copy .claude folder
cp -r "$TMP_DIR/claude-code-hooks-mastery-${BRANCH}/.claude" .

echo -e "${GREEN}Done!${NC}"
echo ""
echo "Installed:"
echo "  .claude/refs/java-patterns.md    - Java 17/21 coding standards"
echo "  .claude/refs/java-testing.md     - Testcontainers, Allure, Selenide"
echo "  .claude/agents/team/builder.md   - Universal builder agent"
echo "  .claude/agents/team/validator.md - Read-only validator agent"
echo "  .claude/hooks/validators/        - Auto-validators for Java/React/Python"
echo ""
echo "Start Claude Code in this directory to use the hooks."
