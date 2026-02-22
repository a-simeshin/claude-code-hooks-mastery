#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Validates plan content for structural correctness before execution.

Hook Type: Stop (3rd in chain after validate_new_file + validate_file_contains)

Checks:
1. Files in `## Relevant Files` exist on disk (except `### New Files`)
2. Task IDs are unique
3. `Depends On` references point to existing Task IDs (no dangling refs)
4. No circular dependencies (DFS with coloring)
5. Agent Types exist in `.claude/agents/team/*.md` (+ built-in types)
6. Acceptance Criteria not empty
7. Every task has a **Stack** field with keywords that route to context sections

Exit codes:
- 0: Validation passed
- 1: Validation failed (structural errors found)

Usage (Stop hook - finds newest file in directory):
  uv run --script validate_plan.py --directory specs --extension .md --team-dir .claude/agents/team

Usage (direct call - specific file):
  uv run --script validate_plan.py --file specs/my-plan.md --team-dir .claude/agents/team
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path

# Logging
SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "validate_plan.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, mode='a')]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DIRECTORY = "specs"
DEFAULT_EXTENSION = ".md"
DEFAULT_MAX_AGE_MINUTES = 5
BUILT_IN_AGENT_TYPES = {
    "general-purpose", "Bash", "Explore", "Plan",
    "statusline-setup", "claude-code-guide", "meta-agent",
}


def get_git_untracked_files(directory: str, extension: str) -> list[str]:
    """Get list of untracked/new files in directory from git."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", f"{directory}/"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return []
        untracked = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            status = line[:2]
            filepath = line[3:].strip()
            if status in ('??', 'A ', ' A', 'AM', ' M', 'M ') and filepath.endswith(extension):
                untracked.append(filepath)
        return untracked
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return []


def get_recent_files(directory: str, extension: str, max_age_minutes: int) -> list[str]:
    """Get list of files modified within the last N minutes."""
    target_dir = Path(directory)
    if not target_dir.exists():
        return []
    recent = []
    now = time.time()
    max_age_seconds = max_age_minutes * 60
    ext = extension if extension.startswith('.') else f'.{extension}'
    for filepath in target_dir.glob(f"*{ext}"):
        try:
            if now - filepath.stat().st_mtime <= max_age_seconds:
                recent.append(str(filepath))
        except OSError:
            continue
    return recent


def find_newest_file(directory: str, extension: str, max_age_minutes: int) -> str | None:
    """Find the most recently created/modified file in directory."""
    git_new = get_git_untracked_files(directory, extension)
    recent_files = get_recent_files(directory, extension, max_age_minutes)
    all_files = list(set(git_new + recent_files))
    if not all_files:
        return None
    newest = None
    newest_mtime = 0
    for filepath in all_files:
        try:
            path = Path(filepath)
            if path.exists():
                mtime = path.stat().st_mtime
                if mtime > newest_mtime:
                    newest_mtime = mtime
                    newest = str(path)
        except OSError:
            continue
    return newest


# ── Plan Parsing ──

def parse_plan(content: str) -> dict:
    """Parse plan markdown into structured data."""
    result = {
        "relevant_files": [],
        "new_files": [],
        "tasks": [],
        "acceptance_criteria": "",
    }

    # Extract Relevant Files (between ## Relevant Files and next ##)
    rf_match = re.search(
        r'^## Relevant Files\s*\n(.*?)(?=^## |\Z)',
        content, re.MULTILINE | re.DOTALL
    )
    if rf_match:
        rf_block = rf_match.group(1)

        # Split into before and after ### New Files
        new_files_match = re.search(
            r'^### New Files\s*\n(.*?)(?=^### |\Z)',
            rf_block, re.MULTILINE | re.DOTALL
        )

        if new_files_match:
            # Files before ### New Files are existing files
            before_new = rf_block[:new_files_match.start()]
            new_block = new_files_match.group(1)
        else:
            before_new = rf_block
            new_block = ""

        # Parse file paths from bullet points (- `path` or - path)
        file_pattern = re.compile(r'^[-*]\s+`([^`]+)`', re.MULTILINE)

        for m in file_pattern.finditer(before_new):
            # Skip subsection headers
            result["relevant_files"].append(m.group(1))

        for m in file_pattern.finditer(new_block):
            result["new_files"].append(m.group(1))

    # Extract Step by Step Tasks
    tasks_match = re.search(
        r'^## Step by Step Tasks\s*\n(.*?)(?=^## |\Z)',
        content, re.MULTILINE | re.DOTALL
    )
    if tasks_match:
        tasks_block = tasks_match.group(1)

        # Split into individual tasks by ### N. headers
        task_sections = re.split(r'^### \d+\.\s+', tasks_block, flags=re.MULTILINE)

        for section in task_sections:
            if not section.strip():
                continue

            task = {}

            # Extract Task ID
            tid = re.search(r'\*\*Task ID\*\*:\s*(.+)', section)
            if tid:
                task["id"] = tid.group(1).strip().strip('`"')

            # Extract Depends On
            dep = re.search(r'\*\*Depends On\*\*:\s*(.+)', section)
            if dep:
                dep_text = dep.group(1).strip()
                if dep_text.lower() in ("none", "-", "n/a", ""):
                    task["depends_on"] = []
                else:
                    # Parse comma-separated or single values, strip backticks/quotes
                    deps = [d.strip().strip('`"') for d in dep_text.split(',')]
                    task["depends_on"] = [d for d in deps if d and d.lower() != "none"]

            # Extract Agent Type
            at = re.search(r'\*\*Agent Type\*\*:\s*(.+)', section)
            if at:
                task["agent_type"] = at.group(1).strip().strip('`"')

            # Extract Stack
            st = re.search(r'\*\*Stack\*\*:\s*(.+)', section)
            if st:
                task["stack"] = st.group(1).strip().strip('`"')

            if "id" in task:
                result["tasks"].append(task)

    # Extract Acceptance Criteria
    ac_match = re.search(
        r'^## Acceptance Criteria\s*\n(.*?)(?=^## |\Z)',
        content, re.MULTILINE | re.DOTALL
    )
    if ac_match:
        result["acceptance_criteria"] = ac_match.group(1).strip()

    return result


# ── Validation Checks ──

def check_relevant_files_exist(relevant_files: list[str], new_files: list[str]) -> list[str]:
    """Check 1: Files in Relevant Files exist on disk (skip New Files)."""
    errors = []
    new_set = set(new_files)
    for f in relevant_files:
        if f in new_set:
            continue
        if not Path(f).exists():
            errors.append(f"File not found: `{f}` (listed in Relevant Files)")
    return errors


def check_unique_task_ids(tasks: list[dict]) -> list[str]:
    """Check 2: Task IDs are unique."""
    errors = []
    seen: dict[str, int] = {}
    for i, task in enumerate(tasks):
        tid = task.get("id", "")
        if not tid:
            errors.append(f"Task #{i+1} has no Task ID")
            continue
        if tid in seen:
            errors.append(f"Duplicate Task ID: `{tid}` (tasks #{seen[tid]} and #{i+1})")
        else:
            seen[tid] = i + 1
    return errors


def check_dependency_refs(tasks: list[dict]) -> list[str]:
    """Check 3: Depends On references point to existing Task IDs."""
    errors = []
    all_ids = {t.get("id") for t in tasks if t.get("id")}
    for task in tasks:
        tid = task.get("id", "?")
        for dep in task.get("depends_on", []):
            if dep not in all_ids:
                errors.append(f"Task `{tid}` depends on `{dep}` which doesn't exist")
    return errors


def check_circular_dependencies(tasks: list[dict]) -> list[str]:
    """Check 4: No circular dependencies (DFS with coloring)."""
    errors = []

    # Build adjacency list
    graph: dict[str, list[str]] = {}
    for task in tasks:
        tid = task.get("id", "")
        if tid:
            graph[tid] = task.get("depends_on", [])

    # DFS with 3 colors: white=unvisited, gray=in-progress, black=done
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {tid: WHITE for tid in graph}

    def dfs(node: str, path: list[str]) -> bool:
        color[node] = GRAY
        path.append(node)
        for dep in graph.get(node, []):
            if dep not in color:
                continue  # dangling ref — caught by check_dependency_refs
            if color[dep] == GRAY:
                # Found cycle
                cycle_start = path.index(dep)
                cycle = path[cycle_start:] + [dep]
                errors.append(f"Circular dependency: {' → '.join(cycle)}")
                return True
            if color[dep] == WHITE:
                if dfs(dep, path):
                    return True
        path.pop()
        color[node] = BLACK
        return False

    for tid in graph:
        if color[tid] == WHITE:
            dfs(tid, [])

    return errors


def check_agent_types(tasks: list[dict], team_dir: str) -> list[str]:
    """Check 5: Agent Types exist in team dir or built-in list."""
    errors = []

    # Discover available agent types from .md files
    team_path = Path(team_dir)
    available: set[str] = set(BUILT_IN_AGENT_TYPES)
    if team_path.exists():
        for md_file in team_path.glob("*.md"):
            # Agent name = filename without extension
            available.add(md_file.stem)

    for task in tasks:
        agent_type = task.get("agent_type", "")
        if not agent_type:
            continue
        if agent_type not in available:
            errors.append(
                f"Task `{task.get('id', '?')}` uses Agent Type `{agent_type}` "
                f"which doesn't exist (available: {', '.join(sorted(available))})"
            )
    return errors


def _load_router():
    """Try to import context_router.route() for Stack keyword validation."""
    try:
        router_path = Path(__file__).parent.parent / "context_router.py"
        if not router_path.exists():
            return None
        import importlib.util
        spec = importlib.util.spec_from_file_location("context_router", str(router_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.route
    except Exception:
        return None


def check_stack_field(tasks: list[dict]) -> list[str]:
    """Check 7: Every task has a Stack field with keywords that actually route."""
    errors = []
    route_fn = _load_router()

    for task in tasks:
        tid = task.get("id", "?")
        stack = task.get("stack", "")

        if not stack or stack.lower() in ("none", "-", "n/a", ""):
            errors.append(
                f"Task `{tid}` has no **Stack** field — "
                "builder won't load coding standards via context routing"
            )
            continue

        # If router is available, verify keywords actually produce sections
        if route_fn:
            result = route_fn(stack)
            if not result.get("sections"):
                errors.append(
                    f"Task `{tid}` Stack \"{stack}\" doesn't match any routing keywords. "
                    "Use: Java, Spring Boot, JPA, Testcontainers, MockMvc, Mockito, "
                    "React, Next.js, Vite, Python, FastAPI, pytest"
                )

    return errors


def check_acceptance_criteria(criteria_text: str) -> list[str]:
    """Check 6: Acceptance Criteria not empty."""
    errors = []
    if not criteria_text:
        errors.append("Acceptance Criteria section is empty")
    elif len(criteria_text.split('\n')) < 2:
        errors.append("Acceptance Criteria has fewer than 2 items — add verifiable criteria")
    return errors


# ── Main Validation ──

def validate_plan(filepath: str, team_dir: str) -> tuple[bool, str]:
    """Run all 6 checks on a plan file."""
    logger.info(f"Validating plan: {filepath}")

    try:
        content = Path(filepath).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        msg = f"Cannot read plan file: {e}"
        logger.error(msg)
        return False, msg

    plan = parse_plan(content)
    logger.info(
        f"Parsed: {len(plan['relevant_files'])} files, "
        f"{len(plan['new_files'])} new files, "
        f"{len(plan['tasks'])} tasks"
    )

    all_errors: list[str] = []

    # Check 1: Relevant files exist
    errs = check_relevant_files_exist(plan["relevant_files"], plan["new_files"])
    if errs:
        logger.warning(f"Check 1 (files exist): {len(errs)} errors")
    all_errors.extend(errs)

    # Check 2: Unique Task IDs
    errs = check_unique_task_ids(plan["tasks"])
    if errs:
        logger.warning(f"Check 2 (unique IDs): {len(errs)} errors")
    all_errors.extend(errs)

    # Check 3: Dependency references valid
    errs = check_dependency_refs(plan["tasks"])
    if errs:
        logger.warning(f"Check 3 (dep refs): {len(errs)} errors")
    all_errors.extend(errs)

    # Check 4: No circular dependencies
    errs = check_circular_dependencies(plan["tasks"])
    if errs:
        logger.warning(f"Check 4 (cycles): {len(errs)} errors")
    all_errors.extend(errs)

    # Check 5: Agent types exist
    errs = check_agent_types(plan["tasks"], team_dir)
    if errs:
        logger.warning(f"Check 5 (agent types): {len(errs)} errors")
    all_errors.extend(errs)

    # Check 6: Acceptance criteria
    errs = check_acceptance_criteria(plan["acceptance_criteria"])
    if errs:
        logger.warning(f"Check 6 (criteria): {len(errs)} errors")
    all_errors.extend(errs)

    # Check 7: Stack field with valid routing keywords
    errs = check_stack_field(plan["tasks"])
    if errs:
        logger.warning(f"Check 7 (stack field): {len(errs)} errors")
    all_errors.extend(errs)

    if all_errors:
        error_list = "\n".join(f"  - {e}" for e in all_errors)
        msg = (
            f"PLAN VALIDATION FAILED: {len(all_errors)} error(s) in '{filepath}'.\n\n"
            f"ERRORS:\n{error_list}\n\n"
            f"ACTION REQUIRED: Fix the errors above in the plan file before proceeding."
        )
        logger.warning(f"FAIL: {len(all_errors)} errors total")
        return False, msg

    msg = f"Plan '{filepath}' passed all 7 structural checks ({len(plan['tasks'])} tasks validated)"
    logger.info(f"PASS: {msg}")
    return True, msg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate plan structural correctness")
    parser.add_argument(
        '-d', '--directory', type=str, default=DEFAULT_DIRECTORY,
        help=f'Directory to scan for newest plan file (default: {DEFAULT_DIRECTORY})'
    )
    parser.add_argument(
        '-e', '--extension', type=str, default=DEFAULT_EXTENSION,
        help=f'File extension to match (default: {DEFAULT_EXTENSION})'
    )
    parser.add_argument(
        '--max-age', type=int, default=DEFAULT_MAX_AGE_MINUTES,
        help=f'Maximum file age in minutes (default: {DEFAULT_MAX_AGE_MINUTES})'
    )
    parser.add_argument(
        '-f', '--file', type=str, default=None,
        help='Direct path to plan file (bypasses directory scanning)'
    )
    parser.add_argument(
        '--team-dir', type=str, default='.claude/agents/team',
        help='Directory with team agent .md files (default: .claude/agents/team)'
    )
    return parser.parse_args()


def main():
    logger.info("=" * 60)
    logger.info("Validator started: validate_plan")

    try:
        args = parse_args()
        logger.info(f"Args: file={args.file}, directory={args.directory}, team_dir={args.team_dir}")

        # Read stdin (hook input)
        try:
            json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError):
            pass

        # Determine which file to validate
        if args.file:
            filepath = args.file
            if not Path(filepath).exists():
                msg = f"Plan file not found: {filepath}"
                logger.error(msg)
                print(json.dumps({"result": "block", "reason": msg}))
                sys.exit(1)
        else:
            filepath = find_newest_file(args.directory, args.extension, args.max_age)
            if not filepath:
                msg = (
                    f"No recent plan file found in {args.directory}/*{args.extension}.\n\n"
                    f"ACTION REQUIRED: Create a plan file in {args.directory}/ first."
                )
                logger.warning(msg)
                print(json.dumps({"result": "block", "reason": msg}))
                sys.exit(1)

        success, message = validate_plan(filepath, args.team_dir)

        if success:
            print(json.dumps({"result": "continue", "message": message}))
            sys.exit(0)
        else:
            print(json.dumps({"result": "block", "reason": message}))
            sys.exit(1)

    except Exception as e:
        logger.exception(f"Validation error: {e}")
        print(json.dumps({
            "result": "continue",
            "message": f"Validation error (allowing through): {str(e)}"
        }))
        sys.exit(0)


if __name__ == "__main__":
    main()
