"""Deterministic generation of a small, runnable agent from a reviewed variant."""

from __future__ import annotations

import json
from pathlib import Path


def generate_agent(variant: dict, destination: Path) -> None:
    """Generate a standard-library-only command-line agent; no provider is invoked."""
    payload = json.dumps(variant, ensure_ascii=False, indent=2)
    code = f'''"""Generated profile-specific conversational agent. Review its source before deployment."""
import argparse
import json

MODEL = json.loads({payload!r})

def reply(message: str) -> dict:
    # A real host may use runtime_context with an approved model provider.
    answer_state = next(state for state in MODEL["states"] if state["id"] == "answer")
    return {{
        "profile": MODEL["profile_id"],
        "reply": answer_state["replies"][0],
        "presentation": MODEL.get("presentation", {{}}),
        "runtime": MODEL.get("runtime", {{}}),
        "input": message,
    }}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    if args.profile != MODEL["profile_id"]:
        raise SystemExit("This generated artifact is bound to a different profile.")
    print(json.dumps(reply(args.message), ensure_ascii=False, indent=2))
'''
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(code, encoding="utf-8")
