#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Status Line v10 - Context Window + Agent Monitor
When no agents running:  [Opus] # [###---] | 42.5% used | ~115k left | session_id
When agents running:     [Opus] [###---] 42% | ▶2 ✓1 | builder(45s) Write Cart.java | builder(32s) Edit App.tsx
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ANSI color codes
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BRIGHT_WHITE = "\033[97m"
DIM = "\033[90m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

EXCLUDED_AGENT_TYPES = {"monitor", "context-router"}


def get_usage_color(percentage: float) -> str:
    if percentage < 50:
        return GREEN
    elif percentage < 75:
        return YELLOW
    elif percentage < 90:
        return RED
    return "\033[91m"


def create_progress_bar(percentage: float, width: int = 10) -> str:
    filled = int((percentage / 100) * width)
    empty = width - filled
    color = get_usage_color(percentage)
    bar = f"{color}{'#' * filled}{DIM}{'-' * empty}{RESET}"
    return f"[{bar}]"


def format_tokens(tokens: int | float | None) -> str:
    if tokens is None:
        return "0"
    if tokens < 1000:
        return str(int(tokens))
    elif tokens < 1000000:
        return f"{tokens / 1000:.0f}k"
    return f"{tokens / 1000000:.1f}M"


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}m{secs:02d}s"


# ─── Agent monitoring ───────────────────────────────────────────

def get_logs_dir() -> Path:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        return Path(project_dir) / "logs"
    return Path.cwd() / "logs"


def load_json_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with open(path) as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def get_last_transcript_action(transcript_path: str, agent_id: str) -> str | None:
    """Read the last tool action from a subagent transcript (fast: reads tail only)."""
    if not transcript_path:
        return None
    base = transcript_path.removesuffix(".jsonl")
    tp = os.path.expanduser(f"{base}/subagents/agent-{agent_id}.jsonl")
    if not os.path.exists(tp):
        return None

    try:
        file_size = os.path.getsize(tp)
        if file_size == 0:
            return None

        # Read last 8KB — enough for several entries
        read_size = min(file_size, 8192)
        with open(tp, "r") as f:
            f.seek(file_size - read_size)
            tail = f.read()

        # Parse lines from the end, find last assistant entry with tool_use
        lines = tail.strip().split("\n")
        for line in reversed(lines):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("type") != "assistant":
                continue

            content = entry.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue

            # Find the last tool_use block
            last_action = None
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name", "")
                inp = block.get("input", {})

                if name in ("Write", "Edit", "MultiEdit"):
                    fp = inp.get("file_path", "")
                    last_action = f"{name} {os.path.basename(fp)}" if fp else name
                elif name == "Read":
                    fp = inp.get("file_path", "")
                    last_action = f"Read {os.path.basename(fp)}" if fp else "Read"
                elif name == "Bash":
                    desc = inp.get("description", "")
                    cmd = inp.get("command", "")
                    label = desc or (cmd[:40] + "…" if len(cmd) > 40 else cmd)
                    last_action = f"Bash: {label}"
                elif name == "Glob":
                    last_action = f"Glob {inp.get('pattern', '')}"
                elif name == "Grep":
                    last_action = f"Grep '{inp.get('pattern', '')}'"
                elif name == "Task":
                    last_action = f"Task: {inp.get('description', '')}"
                else:
                    last_action = name

            if last_action:
                return last_action

    except (OSError, IOError):
        pass
    return None


def get_agent_status() -> dict:
    """Returns {running: [...], done_count: int} with current actions for running agents."""
    logs_dir = get_logs_dir()
    starts = load_json_log(logs_dir / "subagent_start.json")
    stops = load_json_log(logs_dir / "subagent_stop.json")

    # Index starts
    started: dict[str, dict] = {}
    for entry in starts:
        aid = entry.get("agent_id", "")
        atype = entry.get("agent_type", "")
        if aid and atype not in EXCLUDED_AGENT_TYPES:
            started[aid] = entry

    # Index stops
    stopped_ids: set[str] = set()
    for entry in stops:
        aid = entry.get("agent_id", "")
        atype = entry.get("agent_type", "")
        if aid and atype not in EXCLUDED_AGENT_TYPES:
            stopped_ids.add(aid)

    running = []
    done_count = 0

    for aid, entry in started.items():
        if aid in stopped_ids:
            done_count += 1
        else:
            agent_type = entry.get("agent_type", "?")
            started_at = entry.get("logged_at", "")
            duration = 0
            if started_at:
                try:
                    start_dt = datetime.fromisoformat(started_at)
                    duration = max(0, int((datetime.now() - start_dt).total_seconds()))
                except (ValueError, TypeError):
                    pass

            action = get_last_transcript_action(
                entry.get("transcript_path", ""), aid
            )

            running.append({
                "type": agent_type,
                "duration": duration,
                "action": action,
            })

    return {"running": running, "done_count": done_count}


# ─── Status line generation ─────────────────────────────────────

def generate_status_line(input_data: dict) -> str:
    model_info = input_data.get("model", {})
    model_name = model_info.get("display_name", "Claude")

    context_data = input_data.get("context_window", {})
    used_percentage = context_data.get("used_percentage", 0) or 0
    context_window_size = context_data.get("context_window_size", 200000) or 200000
    remaining_tokens = int(context_window_size * ((100 - used_percentage) / 100))

    usage_color = get_usage_color(used_percentage)

    # Check for running agents
    try:
        agents = get_agent_status()
    except Exception:
        agents = {"running": [], "done_count": 0}

    running = agents["running"]
    done_count = agents["done_count"]

    if not running:
        # ── No agents: standard v6 format ──
        session_id = input_data.get("session_id", "") or "--------"
        parts = [
            f"{CYAN}[{model_name}]{RESET}",
            f"{MAGENTA}#{RESET} {create_progress_bar(used_percentage, 15)}",
            f"{usage_color}{used_percentage:.1f}%{RESET} used",
            f"{BLUE}~{format_tokens(remaining_tokens)} left{RESET}",
            f"{DIM}{session_id}{RESET}",
        ]
        return " | ".join(parts)

    # ── Agents active: table format (one agent per row) ──
    lines = []

    # Header line: model + context bar + agent counts
    header_parts = [
        f"{CYAN}[{model_name}]{RESET}",
        f"{create_progress_bar(used_percentage, 8)} {usage_color}{used_percentage:.0f}%{RESET}",
    ]
    counts = []
    if running:
        counts.append(f"{GREEN}▶{len(running)}{RESET}")
    if done_count:
        counts.append(f"{DIM}✓{done_count}{RESET}")
    header_parts.append(" ".join(counts))
    lines.append(" | ".join(header_parts))

    # Agent rows — fixed-width columns for alignment
    max_agents_shown = 5
    for agent in running[:max_agents_shown]:
        atype = agent["type"]
        dur = format_duration(agent["duration"])
        action = agent["action"] or ""

        if len(action) > 50:
            action = action[:47] + "…"

        type_col = f"{atype:<14}"
        dur_col = f"{dur:>6}"

        if action:
            lines.append(f" {GREEN}▶{RESET} {type_col} {DIM}{dur_col}{RESET}  {BRIGHT_WHITE}{action}{RESET}")
        else:
            lines.append(f" {GREEN}▶{RESET} {type_col} {DIM}{dur_col}{RESET}")

    if len(running) > max_agents_shown:
        lines.append(f"   {DIM}+{len(running) - max_agents_shown} more...{RESET}")

    return "\n".join(lines)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        print(generate_status_line(input_data))
        sys.exit(0)
    except json.JSONDecodeError:
        print(f"{RED}[Claude] # Error: Invalid JSON{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}[Claude] # Error: {str(e)}{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
