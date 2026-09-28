"""Command-line entry point for variant derivation and deterministic generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import derive_variant
from .generator import generate_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Derive inspectable personalized agent variants.")
    parser.add_argument("agent", type=Path)
    parser.add_argument("profiles", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    agent = json.loads(args.agent.read_text(encoding="utf-8"))
    profiles = json.loads(args.profiles.read_text(encoding="utf-8"))
    for profile in profiles:
        variant = derive_variant(agent, profile)
        variant_path = args.output / "variants" / f"{profile['id']}.json"
        variant_path.parent.mkdir(parents=True, exist_ok=True)
        variant_path.write_text(json.dumps(variant, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        generate_agent(variant, args.output / "agents" / f"{profile['id']}.py")
        print(f"Derived {variant_path}")


if __name__ == "__main__":
    main()
