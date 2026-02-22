#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Smart Validator Dispatcher for Claude Code PostToolUse Hook.

Reads file_path from stdin JSON, maps file extension to relevant validators,
and runs ONLY matching validators. Replaces 7 separate hook entries with 1.

Savings: ~57% fewer subprocess invocations per Write/Edit operation.

Extension mapping:
  .py          → ruff, ty, bandit
  .java        → spotless, maven_compile (+ jacoco/pmd for test files)
  .ts/.tsx     → eslint, tsc
  .js/.jsx     → eslint, prettier
  .mjs/.cjs    → eslint
  .css/.scss   → prettier
  .json        → prettier
  pom.xml      → maven_compile, ossindex
  other        → no validators (skip)
"""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "validator_dispatcher.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, mode="a")],
)
logger = logging.getLogger(__name__)

# Extension → validator scripts mapping
EXTENSION_MAP: dict[str, list[str]] = {
    ".py": ["ruff_validator.py", "ty_validator.py", "bandit_validator.py"],
    ".java": ["spotless_validator.py", "maven_compile_validator.py"],
    ".ts": ["eslint_validator.py", "tsc_validator.py"],
    ".tsx": ["eslint_validator.py", "tsc_validator.py"],
    ".js": ["eslint_validator.py", "prettier_validator.py"],
    ".jsx": ["eslint_validator.py", "prettier_validator.py"],
    ".mjs": ["eslint_validator.py"],
    ".cjs": ["eslint_validator.py"],
    ".css": ["prettier_validator.py"],
    ".scss": ["prettier_validator.py"],
    ".json": ["prettier_validator.py"],
}


def get_validators_for_file(file_path: str) -> list[str]:
    """Determine which validators to run based on file path."""
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(file_path)

    validators = list(EXTENSION_MAP.get(ext, []))

    # Special case: pom.xml → maven_compile + ossindex
    if filename == "pom.xml":
        validators = ["maven_compile_validator.py", "ossindex_validator.py"]

    # Special case: Java test files → add jacoco and pmd
    if ext == ".java":
        if filename.endswith("Test.java") or filename.endswith("IT.java"):
            validators.append("jacoco_validator.py")
        # PMD for all Java files
        validators.append("pmd_validator.py")

    return validators


def run_validator(validator_script: str, stdin_json: str) -> dict:
    """Run a single validator script, passing stdin JSON. Returns parsed output."""
    validator_path = SCRIPT_DIR / validator_script

    if not validator_path.exists():
        logger.warning(f"Validator not found: {validator_path}")
        return {}

    try:
        result = subprocess.run(
            ["uv", "run", "--script", str(validator_path)],
            input=stdin_json,
            capture_output=True,
            text=True,
            timeout=300,
        )

        stdout = result.stdout.strip()
        if stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                logger.warning(f"{validator_script}: non-JSON output: {stdout[:200]}")
                return {}
        return {}

    except subprocess.TimeoutExpired:
        logger.error(f"{validator_script}: timed out after 300s")
        return {}
    except FileNotFoundError:
        logger.warning(f"uv not found, cannot run {validator_script}")
        return {}


def main():
    logger.info("=" * 60)
    logger.info("VALIDATOR DISPATCHER TRIGGERED")

    # Read stdin JSON (same format all validators expect)
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
        else:
            hook_input = {}
    except json.JSONDecodeError:
        hook_input = {}

    # Extract file_path
    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    if not file_path:
        logger.info("No file_path in input, skipping all validators")
        print(json.dumps({}))
        return

    # Determine which validators to run
    validators = get_validators_for_file(file_path)

    if not validators:
        logger.info(f"No validators for: {file_path}")
        print(json.dumps({}))
        return

    logger.info(f"File: {file_path}")
    logger.info(f"Dispatching to: {validators}")

    # Run matching validators, stop on first block
    for validator_script in validators:
        logger.info(f"Running: {validator_script}")
        result = run_validator(validator_script, stdin_data)

        if result.get("decision") == "block":
            reason = result.get("reason", "Validation failed")
            logger.info(f"BLOCKED by {validator_script}: {reason[:200]}")
            print(json.dumps(result))
            return

    logger.info("All validators passed")
    print(json.dumps({}))


if __name__ == "__main__":
    main()
