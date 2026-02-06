#!/bin/bash
# Uninstall Claude Code hooks
# Usage: curl -fsSL https://raw.githubusercontent.com/.../uninstall.sh | bash -s -- --force
# Or locally: ./uninstall.sh

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

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

if [ "$FORCE" = false ]; then
    # Try to read from terminal directly
    if [ -t 0 ]; then
        read -p "Continue? (y/N) " -n 1 -r
        echo
    else
        # Running via pipe, require --force
        echo ""
        echo -e "${RED}Error: Running via pipe requires --force flag${NC}"
        echo "Usage: curl -fsSL <url>/uninstall.sh | bash -s -- --force"
        exit 1
    fi

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

rm -rf .claude

echo ""
echo -e "${GREEN}Done!${NC}"
echo ".claude directory removed."
