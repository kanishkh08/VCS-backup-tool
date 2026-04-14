#!/usr/bin/env python3
"""
GitVault — Configuration Manager
Member 4: Config & Documentation Developer

Manages per-directory backup settings stored in .git_backup_config.json
inside each target directory.
"""

import json
import os
from pathlib import Path

CONFIG_NAME = ".git_backup_config.json"

# ── Default settings ──────────────────────────────────────────────────────────
DEFAULTS = {
    "interval":              60,           # polling interval in seconds
    "auto_watch":            False,         # start watch automatically on load
    "commit_message_prefix": "[AUTO BACKUP]",
    "ignore_patterns":       [
        ".git", "__pycache__", "*.pyc",
        "*.tmp", ".DS_Store", "Thumbs.db",
        "node_modules", "*.log"
    ],
    "max_log_entries":       50,
    "notify_on_backup":      False,
    "author_name":           "",           # custom git author name
    "author_email":          "",           # custom git author email
}


def get_config_path(directory: str) -> Path:
    """Return path to the config file inside the given directory."""
    return Path(directory) / CONFIG_NAME


def load_config(directory: str) -> dict:
    """Load config for a directory, merging with defaults."""
    path = get_config_path(directory)
    if path.exists():
        try:
            with open(path) as f:
                saved = json.load(f)
            return {**DEFAULTS, **saved}
        except (json.JSONDecodeError, IOError):
            print(f"[CONFIG] Warning: Could not read config at {path}. Using defaults.")
    return dict(DEFAULTS)


def save_config(directory: str, cfg: dict) -> bool:
    """Save config dict to the directory's config file."""
    path = get_config_path(directory)
    try:
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"[CONFIG] Saved to {path}")
        return True
    except IOError as e:
        print(f"[CONFIG] Error saving config: {e}")
        return False


def show_config(directory: str) -> None:
    """Print all current config values for a directory."""
    cfg = load_config(directory)
    print(f"\n{'─'*45}")
    print(f"  Config for: {directory}")
    print(f"{'─'*45}")
    for k, v in cfg.items():
        print(f"  {k:<30} : {v}")
    print(f"{'─'*45}\n")


def set_value(directory: str, key: str, value: str) -> None:
    """Set a single config value, with automatic type conversion."""
    cfg = load_config(directory)
    if key not in DEFAULTS:
        print(f"[CONFIG] Warning: Unknown key '{key}'. Adding anyway.")

    # Auto-convert types
    if value.lower() in ("true", "yes", "1"):
        value = True
    elif value.lower() in ("false", "no", "0"):
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass  # keep as string

    cfg[key] = value
    save_config(directory, cfg)
    print(f"[CONFIG] {key} = {value}")


def reset_config(directory: str) -> None:
    """Reset config to defaults."""
    save_config(directory, dict(DEFAULTS))
    print(f"[CONFIG] Reset to defaults for: {directory}")


def delete_config(directory: str) -> None:
    """Delete the config file for a directory."""
    path = get_config_path(directory)
    if path.exists():
        os.remove(path)
        print(f"[CONFIG] Deleted config at: {path}")
    else:
        print(f"[CONFIG] No config found at: {path}")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="GitVault Config Manager — manage per-directory backup settings"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # show
    sp = sub.add_parser("show", help="Show current config for a directory")
    sp.add_argument("directory", nargs="?", default=".", help="Target directory (default: .)")

    # set
    setp = sub.add_parser("set", help="Set a config value")
    setp.add_argument("directory", help="Target directory")
    setp.add_argument("key",   help="Config key (e.g. interval, auto_watch)")
    setp.add_argument("value", help="New value")

    # reset
    rp = sub.add_parser("reset", help="Reset config to defaults")
    rp.add_argument("directory", nargs="?", default=".")

    # delete
    dp = sub.add_parser("delete", help="Delete config file")
    dp.add_argument("directory", nargs="?", default=".")

    args = parser.parse_args()

    if args.cmd == "show":
        show_config(args.directory)
    elif args.cmd == "set":
        set_value(args.directory, args.key, args.value)
    elif args.cmd == "reset":
        reset_config(args.directory)
    elif args.cmd == "delete":
        delete_config(args.directory)
