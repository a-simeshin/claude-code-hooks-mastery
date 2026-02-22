#!/bin/bash
# Install Claude Code hooks for Java/React projects
# Usage: curl -fsSL https://raw.githubusercontent.com/a-simeshin/claude-code-hooks-mastery/main/install.sh | bash

set -e

REPO="a-simeshin/claude-code-hooks-mastery"
BRANCH="main"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}Claude Code Hooks Installer${NC}"
echo -e "${CYAN}For Java / React / Python projects${NC}"
echo ""

# ─────────────────────────────────────────────────────────────
# Check and install UV (required for hooks)
# ─────────────────────────────────────────────────────────────
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"

    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew install uv
    else
        # Cross-platform installer
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"
    fi

    if command -v uv &> /dev/null; then
        echo -e "${GREEN}UV installed successfully${NC}"
    else
        echo -e "${YELLOW}Warning: UV installation may require restart. Add ~/.local/bin to PATH${NC}"
    fi
else
    echo -e "${GREEN}UV found: $(uv --version)${NC}"
fi
echo ""

# Check if .claude already exists
if [ -d ".claude" ]; then
    echo -e "${YELLOW}Note: .claude directory exists, will merge files${NC}"
fi

# Create temp directory
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Download and extract
echo "Downloading from github.com/${REPO}..."
curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz -C "$TMP_DIR"

# Copy .claude folder (merge if exists)
mkdir -p .claude
cp -r "$TMP_DIR/claude-code-hooks-mastery-${BRANCH}/.claude/." .claude/

echo ""
echo -e "${GREEN}Configuration${NC}"
echo ""

# Detect interactive TTY
if [ -t 0 ] && [ -e /dev/tty ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
    echo -e "${YELLOW}Non-interactive mode: using defaults (status=1, tts=off, agentic=off)${NC}"
fi

# ─────────────────────────────────────────────────────────────
# 1. Status Line
# ─────────────────────────────────────────────────────────────
echo "Status Line options:"
echo "  1) Context window usage bar (default)"
echo "  2) v9 - Minimal powerline style"
echo "  3) v5 - Cost tracking"
echo "  4) Disable"
if [ "$INTERACTIVE" = true ]; then
    read -p "Choose [1-4, default=1]: " STATUS_CHOICE </dev/tty
else
    STATUS_CHOICE="${STATUS_LINE_CHOICE:-1}"
fi

case $STATUS_CHOICE in
    2) STATUS_LINE="status_line_v9.py" ;;
    3) STATUS_LINE="status_line_v5.py" ;;
    4) STATUS_LINE="" ;;
    *) STATUS_LINE="status_line.py" ;;
esac

# ─────────────────────────────────────────────────────────────
# 2. TTS Notifications
# ─────────────────────────────────────────────────────────────
echo ""
if [ "$INTERACTIVE" = true ]; then
    read -p "Enable TTS notifications? (requires ElevenLabs/OpenAI) [y/N]: " -n 1 -r TTS_CHOICE </dev/tty
    echo
else
    TTS_CHOICE="${TTS_ENABLED:-n}"
fi
if [[ $TTS_CHOICE =~ ^[Yy]$ ]]; then
    TTS_ENABLED=true
else
    TTS_ENABLED=false
fi

# ─────────────────────────────────────────────────────────────
# 3. Agentic Mode
# ─────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}Agentic mode runs without permission prompts.${NC}"
if [ "$INTERACTIVE" = true ]; then
    read -p "Start Claude Code with --dangerously-skip-permissions? [y/N]: " -n 1 -r AGENTIC_CHOICE </dev/tty
    echo
else
    AGENTIC_CHOICE="${AGENTIC_MODE:-n}"
fi

# ─────────────────────────────────────────────────────────────
# Apply configuration
# ─────────────────────────────────────────────────────────────
echo ""
SETTINGS_FILE=".claude/settings.json"

# Status Line
if [ -z "$STATUS_LINE" ]; then
    # Remove statusLine section
    sed -i.bak '/"statusLine"/,/^  },/d' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  Status Line: disabled"
elif [ "$STATUS_LINE" != "status_line.py" ]; then
    sed -i.bak "s/status_line\.py/$STATUS_LINE/g" "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  Status Line: $STATUS_LINE"
else
    echo "  Status Line: status_line.py (default)"
fi

# TTS
if [ "$TTS_ENABLED" = false ]; then
    # Remove --notify flags
    sed -i.bak 's/ --notify//g' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  TTS: disabled"
else
    echo "  TTS: enabled"
fi

echo "  Validators: Java, React/TS, Python (all installed)"
echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
echo "Installed to .claude/"

# Launch Claude Code if agentic mode selected
if [[ $AGENTIC_CHOICE =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Starting Claude Code in agentic mode...${NC}"
    exec claude --dangerously-skip-permissions
else
    echo "Run 'claude' to start, or 'claude --dangerously-skip-permissions' for agentic mode."
fi
