#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Verifies that test files written during /smart_build match the plan's
`## Test Infrastructure (User-Declared)` section (Test Realism gate).

For each non-Skipped layer block declared in the plan, checks:
1. Files glob → resolves to ≥1 actual file on disk.
2. Infra signature regex → matches in every resolved file (proving the user-chosen
   infrastructure is actually used, not silently swapped).
3. Happy-path scenarios → each declared scenario has a corresponding test
   (fuzzy grep on the last identifier-like token, e.g., methodName,
   `it` description, or pytest function name).
4. Anti-mock heuristic (integration layer only, WARN-only): if mock count is
   high relative to declared scenarios, warns that the test may be a unit test
   in disguise.

This script is generic — it does not know about specific testing libraries.
It only honors what the plan declared. Add a new infrastructure → just describe
it in the plan, no code change needed here.

Intended to run ONCE at the end of /smart_build, after the per-layer test tasks
complete and before the final validation task. Read-only, no file modifications.

Exit codes:
- 0: All declared layers verified successfully (or only WARNs).
- 1: At least one FAIL (missing files, missing infra signature, missing scenarios).

Usage:
  uv run --script check_test_layers.py --plan specs/my-plan.md
  uv run --script check_test_layers.py --plan specs/my-plan.md --json
"""

import argparse
import importlib.util
import json
import logging
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "check_test_layers.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, mode='a')]
)
logger = logging.getLogger(__name__)

# Anti-mock heuristic patterns. WARN-only, intentionally broad.
MOCK_PATTERNS = [
    r'@MockBean\b',
    r'@Mock\b',
    r'\bMockito\.mock\s*\(',
    r'\bmock\s*\([^)]*\.class\s*\)',
    r'\bmocker\.patch\b',
    r'\bunittest\.mock\b',
    r'\bMagicMock\s*\(',
    r'\bjest\.fn\s*\(',
    r'\bjest\.mock\s*\(',
    r'\bvi\.fn\s*\(',
    r'\bvi\.mock\s*\(',
    r'\bsinon\.stub\s*\(',
]
MOCK_RE = re.compile('|'.join(MOCK_PATTERNS))


def load_parse_plan():
    """Reuse parse_plan() from sibling validate_plan.py to avoid duplication."""
    target = SCRIPT_DIR / "validate_plan.py"
    spec = importlib.util.spec_from_file_location("validate_plan", str(target))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_plan


def resolve_glob(pattern: str) -> list[Path]:
    """Resolve a glob pattern from the project root."""
    root = Path.cwd()
    # Handle both `**/*.ext` and `path/**/*.ext` forms
    matches = list(root.glob(pattern))
    return [p for p in matches if p.is_file()]


def extract_scenario_token(scenario: str) -> str:
    """Extract the most useful grep-able identifier from a scenario string.

    Handles common forms:
      `ClassName#methodName` → `methodName`
      `path/to/test.py::test_func` → `test_func`
      `describe > it desc` → `it desc`
      `it("does X")` → `does X`
      free text → the whole string

    Returns the token to fuzzy-grep for. Caller decides regex strategy.
    """
    s = scenario.strip().strip('`').strip()
    # ClassName#methodName
    if '#' in s:
        return s.rsplit('#', 1)[1].strip()
    # path::test_name
    if '::' in s:
        return s.rsplit('::', 1)[1].strip()
    # describe > it
    if '>' in s:
        return s.rsplit('>', 1)[1].strip()
    # it("...") / test("...")
    m = re.search(r'(?:it|test|describe)\s*\(\s*["\']([^"\']+)["\']', s)
    if m:
        return m.group(1).strip()
    return s


def scenario_found(token: str, files: list[Path]) -> bool:
    """Search the given files for the scenario token."""
    if not token:
        return False
    # Try identifier-like exact match first (word boundary)
    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token):
        pat = re.compile(rf'\b{re.escape(token)}\b')
    else:
        # Free text — case-insensitive, all words must appear
        words = [w for w in re.findall(r'\w+', token) if len(w) > 2]
        if not words:
            return False
        pats = [re.compile(re.escape(w), re.IGNORECASE) for w in words]
        for f in files:
            try:
                txt = f.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            if all(p.search(txt) for p in pats):
                return True
        return False
    for f in files:
        try:
            txt = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        if pat.search(txt):
            return True
    return False


def count_mocks(files: list[Path]) -> tuple[int, int]:
    """Return (mock_occurrences, files_with_mocks) across the given files."""
    total = 0
    files_with = 0
    for f in files:
        try:
            txt = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        hits = len(MOCK_RE.findall(txt))
        if hits:
            total += hits
            files_with += 1
    return total, files_with


def check_layer(layer: dict) -> tuple[list[str], list[str]]:
    """Check a single layer block. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    kind = layer.get("kind", "?")
    stack = layer.get("stack", "?")
    kind_label = "E2E" if kind == "e2e" else kind.capitalize()
    label = f"{kind_label} Layer ({stack})"

    status = (layer.get("status") or "").lower()
    is_skipped = status.startswith("skipped") or status.startswith("opted out") or status.startswith("opt-out")

    if is_skipped:
        if kind == "integration":
            errors.append(
                f"{label}: status `{layer['status']}` — Integration cannot be skipped. "
                "This should have been caught by validate_plan.py Check 10; the plan was edited after validation."
            )
        return errors, warnings

    files_glob = layer.get("files_glob")
    if not files_glob:
        errors.append(f"{label}: no `Files glob` declared.")
        return errors, warnings

    files = resolve_glob(files_glob)
    if not files:
        errors.append(
            f"{label}: glob `{files_glob}` resolved to 0 files. "
            f"The {kind}-tests task did not produce the expected test files, "
            "or the glob pattern in the plan is wrong."
        )
        return errors, warnings

    # Infra signature: required for integration and e2e
    sig = layer.get("infra_signature")
    if sig and sig.lower() not in ("n/a", "none", "-"):
        try:
            sig_re = re.compile(sig)
        except re.error as e:
            errors.append(f"{label}: `Infra signature` is not a valid regex: {e}")
            return errors, warnings
        files_missing_sig = []
        for f in files:
            try:
                txt = f.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            if not sig_re.search(txt):
                files_missing_sig.append(str(f))
        if files_missing_sig:
            sample = ', '.join(files_missing_sig[:3])
            more = f" (+{len(files_missing_sig) - 3} more)" if len(files_missing_sig) > 3 else ""
            errors.append(
                f"{label}: `Infra signature` `{sig}` not found in {len(files_missing_sig)} file(s): {sample}{more}. "
                "The declared infrastructure is not actually used by these tests."
            )
    elif kind in ("integration", "e2e"):
        errors.append(
            f"{label}: `Infra signature` is required for {kind} layer (got `{sig}`). "
            "Declare a regex that proves the chosen infrastructure is in use "
            "(e.g., `@Testcontainers|import org\\.testcontainers`, `@EmbeddedKafka`, `import.*playwright`)."
        )

    # Scenarios: each must be findable
    scenarios = layer.get("scenarios", [])
    if not scenarios:
        errors.append(f"{label}: no Happy-path scenarios declared.")
    else:
        missing = []
        for scenario in scenarios:
            token = extract_scenario_token(scenario)
            if not scenario_found(token, files):
                missing.append(scenario)
        if missing:
            errors.append(
                f"{label}: {len(missing)} declared scenario(s) not found in tests: "
                f"{'; '.join(missing[:5])}{'...' if len(missing) > 5 else ''}. "
                "Either rename the test method/description to match the declared scenario, "
                "or update the scenario string in the plan to match what was actually implemented."
            )

    # Anti-mock heuristic — integration only, WARN-only
    if kind == "integration":
        mocks, files_with = count_mocks(files)
        scen_count = max(1, len(scenarios))
        # Threshold: mocks per scenario > 3 AND files-with-mocks ≥ half of all files
        if mocks > scen_count * 3 and files_with >= max(1, len(files) // 2):
            warnings.append(
                f"{label}: high mock density — {mocks} mock occurrences across "
                f"{files_with}/{len(files)} integration files (~{mocks // scen_count} per scenario). "
                "Verify these are not unit tests in disguise. Mocking external services (HTTP APIs, "
                "third-party SDKs) is fine; mocking internal collaborators in an integration test is "
                "usually a smell."
            )

    return errors, warnings


def check_plan(plan_path: Path) -> tuple[bool, dict]:
    """Run all layer checks. Returns (passed, report_dict)."""
    parse_plan = load_parse_plan()
    try:
        content = plan_path.read_text(encoding='utf-8')
    except OSError as e:
        return False, {"error": f"Cannot read plan: {e}"}

    plan = parse_plan(content)
    test_infra = plan.get("test_infrastructure", {})

    if not test_infra.get("section_present"):
        return False, {
            "error": "Plan has no `## Test Infrastructure (User-Declared)` section. "
                     "Cannot verify test realism without it. Run /plan_w_team to migrate."
        }

    layers = test_infra.get("layers", [])
    if not layers:
        return False, {
            "error": "`## Test Infrastructure (User-Declared)` section has no layer blocks."
        }

    report = {
        "plan": str(plan_path),
        "layers_checked": len(layers),
        "results": [],
        "errors_total": 0,
        "warnings_total": 0,
    }

    overall_pass = True
    for layer in layers:
        errs, warns = check_layer(layer)
        report["results"].append({
            "layer": f"{layer.get('kind')} ({layer.get('stack')})",
            "status": layer.get("status"),
            "errors": errs,
            "warnings": warns,
        })
        report["errors_total"] += len(errs)
        report["warnings_total"] += len(warns)
        if errs:
            overall_pass = False

    return overall_pass, report


def format_human(report: dict) -> str:
    """Render the report as human-readable text."""
    if "error" in report:
        return f"FAIL: {report['error']}"

    lines = [f"Test Layer Realism Check — {report['plan']}"]
    lines.append(f"Layers checked: {report['layers_checked']}")
    lines.append("")
    for r in report["results"]:
        status_tag = "✗" if r["errors"] else ("⚠" if r["warnings"] else "✓")
        status_suffix = f" [{r['status']}]" if r.get("status") else ""
        lines.append(f"  {status_tag} {r['layer']}{status_suffix}")
        for e in r["errors"]:
            lines.append(f"      ERROR: {e}")
        for w in r["warnings"]:
            lines.append(f"      WARN:  {w}")
    lines.append("")
    lines.append(f"Total errors: {report['errors_total']}, warnings: {report['warnings_total']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify test files match the plan's User-Declared test infra section."
    )
    parser.add_argument('--plan', type=str, required=True, help='Path to the plan markdown file.')
    parser.add_argument('--json', action='store_true', help='Output JSON instead of human-readable text.')
    return parser.parse_args()


def main():
    logger.info("=" * 60)
    logger.info("check_test_layers started")

    args = parse_args()
    plan_path = Path(args.plan)
    if not plan_path.exists():
        msg = f"Plan file not found: {plan_path}"
        logger.error(msg)
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        sys.exit(1)

    passed, report = check_plan(plan_path)
    logger.info(f"Result: {'PASS' if passed else 'FAIL'} — {report.get('errors_total', 0)} errors, {report.get('warnings_total', 0)} warnings")

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_human(report))

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
