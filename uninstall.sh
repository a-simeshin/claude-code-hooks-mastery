#!/bin/bash
# Uninstall Claude Code hooks
# Usage: curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/uninstall.sh | bash

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}Claude Code Hooks Uninstaller${NC}"
echo ""

if [ ! -d ".claude" ]; then
    echo "No .claude directory found in current directory."
    exit 0
fi

echo "This will remove:"
echo "  .claude/refs/"
echo "  .claude/agents/team/"
echo "  .claude/hooks/validators/"
echo "  .claude/settings.json"
echo "  .claude/status_lines/"
echo "  .claude/output-styles/"
echo "  .claude/commands/"
echo ""
echo -e "${YELLOW}Warning: This will delete the entire .claude directory!${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

rm -rf .claude

echo ""
echo -e "${GREEN}Done!${NC}"
echo ".claude directory removed."
