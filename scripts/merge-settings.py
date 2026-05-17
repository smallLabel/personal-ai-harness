#!/usr/bin/env python3
"""Merge (or remove) a hooks block into ~/.claude/settings.json.

Preserves all other top-level keys (env, model, permissions, etc.).
Deduplicates by command string, so re-running is safe.
"""
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text() or "{}")
    except json.JSONDecodeError as e:
        print(f"  ✗ malformed JSON at {path}: {e}", file=sys.stderr)
        sys.exit(1)


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path.with_name(path.name + f".backup.{stamp}")
    shutil.copy2(path, bak)
    print(f"  ⚠ backed up: {bak}")
    return bak


def commands_in(config: dict) -> set[str]:
    return {
        h.get("command", "")
        for h in config.get("hooks", [])
        if h.get("type") == "command"
    }


def merge_hooks(target_hooks: dict, source_hooks: dict) -> dict:
    out = {k: list(v) for k, v in target_hooks.items()}
    for event, configs in source_hooks.items():
        out.setdefault(event, [])
        existing = set()
        for cfg in out[event]:
            existing |= commands_in(cfg)
        for cfg in configs:
            new_cmds = commands_in(cfg)
            if new_cmds & existing:
                print(f"  • already present, skip: [{event}] {sorted(new_cmds)}")
                continue
            out[event].append(cfg)
            print(f"  + added: [{event}] {sorted(new_cmds)}")
    return out


def remove_hooks(target_hooks: dict, source_hooks: dict) -> dict:
    out = {k: list(v) for k, v in target_hooks.items()}
    to_remove = {
        event: commands_in({"hooks": [h for cfg in configs for h in cfg.get("hooks", [])]})
        for event, configs in source_hooks.items()
    }
    for event, cmds in to_remove.items():
        if event not in out:
            continue
        kept = []
        for cfg in out[event]:
            cfg_cmds = commands_in(cfg)
            if cfg_cmds & cmds:
                print(f"  - removed: [{event}] {sorted(cfg_cmds & cmds)}")
                continue
            kept.append(cfg)
        if kept:
            out[event] = kept
        else:
            del out[event]
            print(f"  - removed empty [{event}] block")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", required=True, help="path to user's settings.json")
    p.add_argument("--source", required=True, help="path to settings.hooks.json with new hooks")
    p.add_argument("--remove", action="store_true", help="remove hooks listed in source rather than add")
    args = p.parse_args()

    target_path = Path(args.target)
    source_path = Path(args.source)

    if not source_path.exists():
        print(f"  ✗ source missing: {source_path}", file=sys.stderr)
        return 1

    source = load(source_path)
    source_hooks = source.get("hooks", {})
    if not source_hooks:
        print(f"  ✗ source has no \"hooks\" key: {source_path}", file=sys.stderr)
        return 1

    backup(target_path)
    target = load(target_path)
    target_hooks = target.get("hooks", {})

    if args.remove:
        new_hooks = remove_hooks(target_hooks, source_hooks)
    else:
        new_hooks = merge_hooks(target_hooks, source_hooks)

    if new_hooks:
        target["hooks"] = new_hooks
    elif "hooks" in target:
        del target["hooks"]

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(target, indent=2) + "\n")
    print(f"  ✓ wrote: {target_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
