#!/bin/bash
# Uninstall Claude Code hooks (only files installed by install.sh)
# Usage: ./uninstall.sh
# Or:    curl -fsSL <url>/uninstall.sh | bash -s -- --force

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
DIM='\033[0;90m'
NC='\033[0m'

FORCE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f) FORCE=true; shift ;;
        *) shift ;;
    esac
done

echo -e "${RED}Claude Code Hooks Uninstaller${NC}"
echo ""

if [ ! -d ".claude" ]; then
    echo "No .claude directory found."
    exit 0
fi

# ─────────────────────────────────────────────────────────────
# Exactly what install.sh puts in place
# ─────────────────────────────────────────────────────────────

# Directories owned entirely by this extension
OWNED_DIRS=(
    .claude/hooks
    .claude/status_lines
    .claude/output-styles
    .claude/refs
)

# Individual files in shared directories
OWNED_FILES=(
    # agents
    .claude/agents/context-router.md
    .claude/agents/meta-agent.md
    .claude/agents/team/builder.md
    .claude/agents/team/plan-reviewer.md
    .claude/agents/team/validator.md
    # commands
    .claude/commands/all_tools.md
    .claude/commands/build.md
    .claude/commands/git_status.md
    .claude/commands/plan_w_team.md
    .claude/commands/plan.md
    .claude/commands/question.md
    .claude/commands/smart_build.md
    .claude/commands/update_status_line.md
    # settings
    .claude/settings.json
)

# Show what will be removed
echo "Will remove:"
for dir in "${OWNED_DIRS[@]}"; do
    [ -d "$dir" ] && echo -e "  ${RED}$dir/${NC}"
done
for file in "${OWNED_FILES[@]}"; do
    [ -f "$file" ] && echo -e "  ${RED}$file${NC}"
done

# Show what will be kept
echo ""
echo -e "Will ${GREEN}keep${NC} (not ours):"
KEPT=false
for item in .claude/*; do
    [ ! -e "$item" ] && continue
    basename=$(basename "$item")
    # Skip items we own
    case "$basename" in
        hooks|status_lines|output-styles|refs|settings.json) continue ;;
    esac
    echo -e "  ${GREEN}$item${NC}"
    KEPT=true
done
# Check for user files in agents/ and commands/ that aren't ours
for dir in .claude/agents .claude/commands; do
    [ ! -d "$dir" ] && continue
    while IFS= read -r -d '' file; do
        is_ours=false
        for owned in "${OWNED_FILES[@]}"; do
            [ "$file" = "$owned" ] && is_ours=true && break
        done
        if [ "$is_ours" = false ]; then
            echo -e "  ${GREEN}$file${NC}"
            KEPT=true
        fi
    done < <(find "$dir" -type f -print0 2>/dev/null)
done
if [ "$KEPT" = false ]; then
    echo -e "  ${DIM}(nothing extra found)${NC}"
fi

# Confirm
echo ""
if [ "$FORCE" = false ]; then
    if [ -t 0 ]; then
        read -p "Continue? (y/N) " -n 1 -r
        echo
    else
        echo -e "${RED}Error: Running via pipe requires --force flag${NC}"
        echo "Usage: curl -fsSL <url>/uninstall.sh | bash -s -- --force"
        exit 1
    fi
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# ─────────────────────────────────────────────────────────────
# Remove owned directories
# ─────────────────────────────────────────────────────────────
for dir in "${OWNED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo -e "  Removed ${RED}$dir/${NC}"
    fi
done

# ─────────────────────────────────────────────────────────────
# Remove owned files
# ─────────────────────────────────────────────────────────────
for file in "${OWNED_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "  Removed ${RED}$file${NC}"
    fi
done

# ─────────────────────────────────────────────────────────────
# Clean up empty directories (but never .claude/ itself)
# ─────────────────────────────────────────────────────────────
for dir in .claude/agents/team .claude/agents .claude/commands; do
    if [ -d "$dir" ] && [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
        rmdir "$dir"
        echo -e "  Removed empty ${DIM}$dir/${NC}"
    fi
done

echo ""
echo -e "${GREEN}Done!${NC}"

# Check if .claude/ is now empty
if [ -d ".claude" ] && [ -z "$(ls -A .claude 2>/dev/null)" ]; then
    rmdir .claude
    echo ".claude/ was empty, removed."
else
    echo ".claude/ kept — contains your files."
fi
