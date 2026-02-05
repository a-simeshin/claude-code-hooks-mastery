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

echo ""
echo -e "${GREEN}Configuration${NC}"
echo ""

# ─────────────────────────────────────────────────────────────
# 1. Status Line
# ─────────────────────────────────────────────────────────────
echo "Status Line options:"
echo "  1) v6 - Context window usage bar (default)"
echo "  2) v9 - Minimal powerline style"
echo "  3) v5 - Cost tracking"
echo "  4) v3 - Agent sessions with history"
echo "  5) Disable"
read -p "Choose [1-5, default=1]: " STATUS_CHOICE

case $STATUS_CHOICE in
    2) STATUS_LINE="status_line_v9.py" ;;
    3) STATUS_LINE="status_line_v5.py" ;;
    4) STATUS_LINE="status_line_v3.py" ;;
    5) STATUS_LINE="" ;;
    *) STATUS_LINE="status_line_v6.py" ;;
esac

# ─────────────────────────────────────────────────────────────
# 2. TTS Notifications
# ─────────────────────────────────────────────────────────────
echo ""
read -p "Enable TTS notifications? (requires ElevenLabs/OpenAI) [y/N]: " -n 1 -r TTS_CHOICE
echo
if [[ $TTS_CHOICE =~ ^[Yy]$ ]]; then
    TTS_ENABLED=true
else
    TTS_ENABLED=false
fi

# ─────────────────────────────────────────────────────────────
# 3. Stack selection
# ─────────────────────────────────────────────────────────────
echo ""
echo "Which stacks do you need validators for?"
read -p "  Java (Spotless, Maven)? [Y/n]: " -n 1 -r JAVA_CHOICE
echo
read -p "  React/TypeScript (ESLint, TSC)? [Y/n]: " -n 1 -r REACT_CHOICE
echo
read -p "  Python (Ruff, Bandit)? [Y/n]: " -n 1 -r PYTHON_CHOICE
echo

# ─────────────────────────────────────────────────────────────
# Apply configuration
# ─────────────────────────────────────────────────────────────
SETTINGS_FILE=".claude/settings.json"

# Status Line
if [ -z "$STATUS_LINE" ]; then
    # Remove statusLine section
    sed -i.bak '/"statusLine"/,/^  },/d' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  Status Line: disabled"
elif [ "$STATUS_LINE" != "status_line_v6.py" ]; then
    sed -i.bak "s/status_line_v6.py/$STATUS_LINE/g" "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  Status Line: $STATUS_LINE"
else
    echo "  Status Line: status_line_v6.py (default)"
fi

# TTS
if [ "$TTS_ENABLED" = false ]; then
    # Remove --notify flags
    sed -i.bak 's/ --notify//g' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  TTS: disabled"
else
    echo "  TTS: enabled"
fi

# Remove unused validators
if [[ ! $JAVA_CHOICE =~ ^[Yy]?$ ]] || [[ $JAVA_CHOICE == "n" ]] || [[ $JAVA_CHOICE == "N" ]]; then
    rm -f .claude/hooks/validators/spotless_validator.py
    rm -f .claude/hooks/validators/maven_compile_validator.py
    rm -f .claude/hooks/validators/jacoco_validator.py
    rm -f .claude/hooks/validators/pmd_validator.py
    rm -f .claude/hooks/validators/ossindex_validator.py
    echo "  Java validators: removed"
else
    echo "  Java validators: installed"
fi

if [[ ! $REACT_CHOICE =~ ^[Yy]?$ ]] || [[ $REACT_CHOICE == "n" ]] || [[ $REACT_CHOICE == "N" ]]; then
    rm -f .claude/hooks/validators/eslint_validator.py
    rm -f .claude/hooks/validators/tsc_validator.py
    rm -f .claude/hooks/validators/prettier_validator.py
    echo "  React/TS validators: removed"
else
    echo "  React/TS validators: installed"
fi

if [[ ! $PYTHON_CHOICE =~ ^[Yy]?$ ]] || [[ $PYTHON_CHOICE == "n" ]] || [[ $PYTHON_CHOICE == "N" ]]; then
    rm -f .claude/hooks/validators/ruff_validator.py
    rm -f .claude/hooks/validators/ty_validator.py
    rm -f .claude/hooks/validators/bandit_validator.py
    echo "  Python validators: removed"
else
    echo "  Python validators: installed"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
echo "Installed to .claude/"
echo "Start Claude Code in this directory to use the hooks."
