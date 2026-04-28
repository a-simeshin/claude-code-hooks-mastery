#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Verifies that git changes match the plan's declared scope (Surgical Scope check).

Compares files modified in the working tree (and optionally vs a baseline ref)
against the plan's `## Relevant Files` + `### New Files`. Anything outside that
list is reported as an unrelated change.

Intended to run ONCE at the end of plan execution (final validation step), not
on every Write/Edit. Read-only.

Exit codes:
- 0: All changes are in scope (or no plan/git available — silent skip)
- 1: Out-of-scope changes detected (advisory; caller decides whether to block)

Usage:
  uv run --script check_diff_scope.py --plan specs/my-plan.md
  uv run --script check_diff_scope.py --plan specs/my-plan.md --baseline main
  uv run --script check_diff_scope.py --plan specs/my-plan.md --json
"""

import argparse
import importlib.util
import json
import logging
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "check_diff_scope.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, mode='a')]
)
logger = logging.getLogger(__name__)

# Files always ignored — tooling artifacts, the plan itself, logs.
DEFAULT_IGNORE_PREFIXES = (
    ".git/",
    "specs/",
    "logs/",
)
DEFAULT_IGNORE_SUFFIXES = (
    ".log",
)


def load_parse_plan():
    """Import parse_plan() from sibling validate_plan.py to avoid duplication."""
    target = SCRIPT_DIR / "validate_plan.py"
    spec = importlib.util.spec_from_file_location("validate_plan", str(target))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_plan


def get_changed_files(baseline: str | None) -> list[str]:
    """Collect changed files: working tree + index, optionally vs a baseline ref."""
    files: set[str] = set()

    # Working tree + index changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                # Format: XY path  (or XY orig -> new for renames)
                path = line[3:].strip()
                if "->" in path:
                    path = path.split("->")[-1].strip()
                files.add(path)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.warning(f"git status failed: {e}")

    # Optional: diff against a baseline ref (e.g. branch point)
    if baseline:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", baseline],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.strip():
                        files.add(line.strip())
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"git diff vs {baseline} failed: {e}")

    return sorted(files)


def is_ignored(path: str) -> bool:
    if any(path.startswith(p) for p in DEFAULT_IGNORE_PREFIXES):
        return True
    if any(path.endswith(s) for s in DEFAULT_IGNORE_SUFFIXES):
        return True
    return False


def classify(changed: list[str], in_scope: set[str]) -> tuple[list[str], list[str]]:
    """Split changed files into (in_scope, out_of_scope), ignoring boilerplate."""
    in_list: list[str] = []
    out_list: list[str] = []
    for path in changed:
        if is_ignored(path):
            continue
        if path in in_scope:
            in_list.append(path)
        else:
            out_list.append(path)
    return in_list, out_list


def main():
    parser = argparse.ArgumentParser(
        description="Verify git changes match the plan's declared scope."
    )
    parser.add_argument("--plan", required=True, help="Path to the plan markdown file")
    parser.add_argument(
        "--baseline", default=None,
        help="Optional git ref to diff against (e.g. main, HEAD~5). "
             "If omitted, only working tree + index are inspected."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit a JSON report instead of human-readable text"
    )
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        msg = f"Plan file not found: {plan_path}"
        logger.warning(msg)
        print(msg, file=sys.stderr)
        sys.exit(0)  # silent skip — don't block when plan is missing

    try:
        parse_plan = load_parse_plan()
        plan = parse_plan(plan_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.exception("parse_plan failed")
        print(f"Could not parse plan: {e}", file=sys.stderr)
        sys.exit(0)

    in_scope: set[str] = set(plan["relevant_files"]) | set(plan["new_files"])
    if not in_scope:
        msg = f"Plan {plan_path} declares no Relevant Files — skipping scope check"
        logger.info(msg)
        print(msg, file=sys.stderr)
        sys.exit(0)

    changed = get_changed_files(args.baseline)
    in_list, out_list = classify(changed, in_scope)

    logger.info(
        f"plan={plan_path} baseline={args.baseline} "
        f"declared={len(in_scope)} changed={len(changed)} "
        f"in_scope={len(in_list)} out_of_scope={len(out_list)}"
    )

    if args.json:
        print(json.dumps({
            "plan": str(plan_path),
            "baseline": args.baseline,
            "declared_scope": sorted(in_scope),
            "in_scope_changes": in_list,
            "out_of_scope_changes": out_list,
            "verdict": "PASS" if not out_list else "FAIL",
        }, indent=2))
    else:
        print(f"Plan: {plan_path}")
        print(f"Baseline: {args.baseline or '(working tree + index only)'}")
        print(f"Declared scope: {len(in_scope)} files")
        print(f"In-scope changes ({len(in_list)}):")
        for f in in_list:
            print(f"  ✓ {f}")
        if out_list:
            print(f"\nOut-of-scope changes ({len(out_list)}):")
            for f in out_list:
                print(f"  ✗ {f}")
            print(
                "\nVerdict: FAIL — these files were modified but not declared in "
                "## Relevant Files / ### New Files. Either add them to the plan "
                "(if intentional) or revert (if scope creep)."
            )
        else:
            print("\nVerdict: PASS — all changes are within declared scope.")

    sys.exit(0 if not out_list else 1)


if __name__ == "__main__":
    main()
