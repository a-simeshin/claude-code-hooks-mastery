#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

"""
Monitor Check — reads subagent logs and transcripts, outputs compact JSON summary.

Used by the monitor agent to get status of all running/completed sub-agents
without expensive LLM-based parsing. All heavy logic lives here.

Usage:
    uv run --no-project .claude/hooks/monitor_check.py
    uv run --no-project .claude/hooks/monitor_check.py --reset  # clear state
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


LOGS_DIR = Path.cwd() / "logs"
START_LOG = LOGS_DIR / "subagent_start.json"
STOP_LOG = LOGS_DIR / "subagent_stop.json"
STATE_FILE = LOGS_DIR / "monitor_state.json"

# Agent types to exclude from monitoring (the monitor itself)
EXCLUDED_TYPES = {"monitor"}


def load_json_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with open(path) as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"offsets": {}, "last_actions": {}}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"offsets": {}, "last_actions": {}}


def save_state(state: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def construct_transcript_path(transcript_path: str, agent_id: str) -> str | None:
    """Construct subagent transcript path from main session transcript path + agent_id."""
    if not transcript_path:
        return None
    # Main transcript: ~/.claude/projects/.../abc123.jsonl
    # Subagent transcript: ~/.claude/projects/.../abc123/subagents/agent-{agent_id}.jsonl
    base = transcript_path.removesuffix(".jsonl")
    path = f"{base}/subagents/agent-{agent_id}.jsonl"
    expanded = os.path.expanduser(path)
    return expanded if os.path.exists(expanded) else None


def parse_tool_action(content_block: dict) -> str | None:
    """Extract a human-readable action from a tool_use content block."""
    if content_block.get("type") != "tool_use":
        return None

    name = content_block.get("name", "")
    inp = content_block.get("input", {})

    if name in ("Write", "Edit", "MultiEdit"):
        file_path = inp.get("file_path", "")
        filename = os.path.basename(file_path) if file_path else "?"
        return f"{name} {filename}"

    if name == "Read":
        file_path = inp.get("file_path", "")
        filename = os.path.basename(file_path) if file_path else "?"
        return f"Read {filename}"

    if name == "Bash":
        cmd = inp.get("command", "")
        desc = inp.get("description", "")
        label = desc if desc else (cmd[:60] + "..." if len(cmd) > 60 else cmd)
        return f"Bash: {label}"

    if name == "Glob":
        pattern = inp.get("pattern", "")
        return f"Glob {pattern}"

    if name == "Grep":
        pattern = inp.get("pattern", "")
        return f"Grep '{pattern}'"

    if name in ("TaskList", "TaskGet", "TaskUpdate", "TaskCreate"):
        return f"{name}"

    if name == "Task":
        desc = inp.get("description", "launch agent")
        return f"Task: {desc}"

    return name


def read_new_transcript_entries(transcript_path: str, offset: int) -> tuple[list[dict], int]:
    """Read new JSONL entries from transcript starting at byte offset.
    Returns (new_entries, new_offset)."""
    entries = []
    try:
        file_size = os.path.getsize(transcript_path)
        if file_size <= offset:
            return [], offset

        with open(transcript_path, "r") as f:
            f.seek(offset)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            new_offset = f.tell()
        return entries, new_offset
    except (OSError, IOError):
        return [], offset


def extract_actions_from_entries(entries: list[dict]) -> tuple[list[str], str | None]:
    """Extract recent actions and current action from new transcript entries.
    Returns (recent_actions, current_action)."""
    actions: list[str] = []
    current: str | None = None

    for entry in entries:
        entry_type = entry.get("type", "")

        if entry_type == "assistant":
            message = entry.get("message", {})
            content = message.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        action = parse_tool_action(block)
                        if action:
                            actions.append(action)
                            current = action

    # Deduplicate consecutive same actions
    deduped: list[str] = []
    for a in actions:
        if not deduped or deduped[-1] != a:
            deduped.append(a)

    # Keep last 5 actions max
    recent = deduped[-5:] if len(deduped) > 5 else deduped

    return recent, current


def compute_duration(started_at: str, ended_at: str | None = None) -> int:
    """Compute duration in seconds from ISO timestamp to now or ended_at."""
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(ended_at) if ended_at else datetime.now()
        return max(0, int((end - start).total_seconds()))
    except (ValueError, TypeError):
        return 0


def main() -> None:
    if "--reset" in sys.argv:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        print(json.dumps({"reset": True}))
        return

    # Load logs
    starts = load_json_log(START_LOG)
    stops = load_json_log(STOP_LOG)
    state = load_state()

    # Index by agent_id
    started: dict[str, dict] = {}
    for entry in starts:
        aid = entry.get("agent_id", "")
        atype = entry.get("agent_type", "")
        if aid and atype not in EXCLUDED_TYPES:
            started[aid] = entry

    stopped: dict[str, dict] = {}
    for entry in stops:
        aid = entry.get("agent_id", "")
        atype = entry.get("agent_type", "")
        if aid and atype not in EXCLUDED_TYPES:
            stopped[aid] = entry

    # Build agent reports
    agents = []
    offsets = state.get("offsets", {})

    for aid, start_entry in started.items():
        agent_type = start_entry.get("agent_type", "unknown")
        started_at = start_entry.get("logged_at", "")
        transcript_path = start_entry.get("transcript_path", "")

        if aid in stopped:
            # Agent is done
            stop_entry = stopped[aid]
            ended_at = stop_entry.get("logged_at", "")
            duration = compute_duration(started_at, ended_at)

            # Get summary from last_assistant_message
            last_msg = stop_entry.get("last_assistant_message", "")
            summary = last_msg[:120] + "..." if len(last_msg) > 120 else last_msg
            if not summary:
                summary = "Completed"

            agents.append({
                "agent_id": aid,
                "agent_type": agent_type,
                "status": "done",
                "duration_s": duration,
                "summary": summary,
            })
        else:
            # Agent is running — read transcript
            duration = compute_duration(started_at)
            tp = construct_transcript_path(transcript_path, aid)

            recent_actions: list[str] = []
            current_action: str | None = None

            if tp:
                prev_offset = offsets.get(aid, 0)
                new_entries, new_offset = read_new_transcript_entries(tp, prev_offset)
                offsets[aid] = new_offset

                if new_entries:
                    recent_actions, current_action = extract_actions_from_entries(new_entries)

            agents.append({
                "agent_id": aid,
                "agent_type": agent_type,
                "status": "running",
                "duration_s": duration,
                "recent_actions": recent_actions,
                "current_action": current_action,
            })

    # Save state
    state["offsets"] = offsets
    save_state(state)

    # Determine if all done
    running_count = sum(1 for a in agents if a["status"] == "running")
    done_count = sum(1 for a in agents if a["status"] == "done")

    result = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agents": agents,
        "running": running_count,
        "done": done_count,
        "all_done": running_count == 0 and done_count > 0,
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
