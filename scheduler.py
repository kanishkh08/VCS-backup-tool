#!/usr/bin/env python3
"""
GitVault — OS-Level Scheduler Helper
Member 4: Config & Documentation Developer

Generates shell scripts (Linux/macOS) and batch files (Windows)
for automating backups via OS-level schedulers (cron / Task Scheduler).
Also manages a local job registry for multiple backup directories.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Job registry stored in user's home directory
REGISTRY_FILE = Path.home() / ".gitvault_scheduler.json"


# ── Job Registry ──────────────────────────────────────────────────────────────

def load_registry() -> dict:
    """Load the job registry from disk."""
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"jobs": []}


def save_registry(reg: dict) -> None:
    """Save the job registry to disk."""
    with open(REGISTRY_FILE, "w") as f:
        json.dump(reg, f, indent=2)


def add_job(directory: str, interval: int = 60, message: str = "") -> None:
    """Register a new backup job."""
    reg = load_registry()
    # Check for duplicates
    for job in reg["jobs"]:
        if job["directory"] == os.path.abspath(directory):
            print(f"[SCHEDULER] Job already exists for: {directory}")
            return
    job = {
        "directory": os.path.abspath(directory),
        "interval":  interval,
        "message":   message,
        "added":     datetime.now().isoformat(),
        "active":    True,
    }
    reg["jobs"].append(job)
    save_registry(reg)
    print(f"[SCHEDULER] Job added: '{directory}' every {interval}s")


def list_jobs() -> None:
    """List all registered backup jobs."""
    reg = load_registry()
    if not reg["jobs"]:
        print("[SCHEDULER] No jobs registered.")
        return
    print(f"\n{'─'*60}")
    print(f"  Registered Backup Jobs")
    print(f"{'─'*60}")
    for i, job in enumerate(reg["jobs"], 1):
        status = "✓ Active" if job.get("active") else "✗ Inactive"
        print(f"  {i}. {job['directory']}")
        print(f"     Interval : {job['interval']}s  |  Status: {status}")
        print(f"     Added    : {job['added'][:10]}")
        if job.get("message"):
            print(f"     Message  : {job['message']}")
    print(f"{'─'*60}\n")


def remove_job(index: int) -> None:
    """Remove a job by its list index (1-based)."""
    reg = load_registry()
    if 0 < index <= len(reg["jobs"]):
        removed = reg["jobs"].pop(index - 1)
        save_registry(reg)
        print(f"[SCHEDULER] Removed job: {removed['directory']}")
    else:
        print(f"[SCHEDULER] No job at index {index}.")


# ── Script Generators ─────────────────────────────────────────────────────────

def generate_shell_script(
    directory: str,
    interval: int = 60,
    output:   str = "run_backup.sh"
) -> None:
    """
    Generate a shell script for Linux/macOS cron.
    Add to crontab with: crontab -e
    Then add:  * * * * * /bin/bash /path/to/run_backup.sh
    """
    backend = Path(__file__).parent / "backend" / "app.py"
    runner  = Path(__file__).parent / "run.py"

    content = f"""#!/bin/bash
# ─────────────────────────────────────────────────────────
# GitVault — Auto Backup Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Directory: {directory}
# Interval : {interval} seconds
# ─────────────────────────────────────────────────────────
# To add to crontab:
#   crontab -e
#   Then add this line (runs every minute):
#   * * * * * /bin/bash {os.path.abspath(output)}
# ─────────────────────────────────────────────────────────

BACKUP_DIR="{os.path.abspath(directory)}"
INTERVAL={interval}
PYTHON=$(which python3 || which python)
SCRIPT="{backend}"

if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python not found." >> ~/gitvault_backup.log
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "[ERROR] Directory not found: $BACKUP_DIR" >> ~/gitvault_backup.log
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup check running..." >> ~/gitvault_backup.log
$PYTHON "$SCRIPT" watch "$BACKUP_DIR" --interval "$INTERVAL" &
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Watch started (PID: $!)" >> ~/gitvault_backup.log
"""
    with open(output, "w") as f:
        f.write(content)
    os.chmod(output, 0o755)
    print(f"[SCHEDULER] Shell script written to: {os.path.abspath(output)}")
    print(f"            Add to crontab: * * * * * /bin/bash {os.path.abspath(output)}")


def generate_bat_script(
    directory: str,
    interval: int = 60,
    output:   str = "run_backup.bat"
) -> None:
    """
    Generate a Windows batch file for Task Scheduler.
    Import into Task Scheduler → Create Basic Task → trigger: Daily/On startup.
    """
    backend = Path(__file__).parent / "backend" / "app.py"

    content = f"""@echo off
REM ─────────────────────────────────────────────────────────
REM GitVault — Auto Backup Script (Windows)
REM Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
REM Directory: {directory}
REM Interval : {interval} seconds
REM ─────────────────────────────────────────────────────────
REM To use with Task Scheduler:
REM   1. Open Task Scheduler
REM   2. Create Basic Task
REM   3. Set trigger: At startup or Daily
REM   4. Set action: Start a program → this .bat file
REM ─────────────────────────────────────────────────────────

set BACKUP_DIR={os.path.abspath(directory)}
set INTERVAL={interval}
set SCRIPT={backend}

if not exist "%BACKUP_DIR%" (
    echo [ERROR] Directory not found: %BACKUP_DIR%
    exit /b 1
)

echo [%DATE% %TIME%] Starting GitVault backup watch...
python "%SCRIPT%" watch "%BACKUP_DIR%" --interval %INTERVAL%
"""
    with open(output, "w") as f:
        f.write(content)
    print(f"[SCHEDULER] Batch file written to: {os.path.abspath(output)}")
    print("            Import into Windows Task Scheduler to automate.")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="GitVault Scheduler Helper — generate OS scripts and manage backup jobs"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add job
    ap = sub.add_parser("add", help="Register a backup job")
    ap.add_argument("directory")
    ap.add_argument("-i", "--interval", type=int, default=60)
    ap.add_argument("-m", "--message", default="")

    # list jobs
    sub.add_parser("list", help="List registered jobs")

    # remove job
    rp = sub.add_parser("remove", help="Remove a job by index")
    rp.add_argument("index", type=int)

    # generate shell script
    gsh = sub.add_parser("gen-sh", help="Generate Linux/macOS shell script")
    gsh.add_argument("directory")
    gsh.add_argument("-i", "--interval", type=int, default=60)
    gsh.add_argument("-o", "--output", default="run_backup.sh")

    # generate bat file
    gbat = sub.add_parser("gen-bat", help="Generate Windows batch file")
    gbat.add_argument("directory")
    gbat.add_argument("-i", "--interval", type=int, default=60)
    gbat.add_argument("-o", "--output", default="run_backup.bat")

    args = parser.parse_args()

    if args.cmd == "add":
        add_job(args.directory, args.interval, args.message)
    elif args.cmd == "list":
        list_jobs()
    elif args.cmd == "remove":
        remove_job(args.index)
    elif args.cmd == "gen-sh":
        generate_shell_script(args.directory, args.interval, args.output)
    elif args.cmd == "gen-bat":
        generate_bat_script(args.directory, args.interval, args.output)
