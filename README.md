# GitVault — Git-based File Backup Tool

A complete **frontend + backend** web application that uses Git as a versioning engine to automate backups of any local directory.

---

## Team Members

| Member | Name | URN | Role | Contribution |
|--------|------|-----|------|-------------|
| Member 1 (Lead) | ________________ | ________________ | Backend Developer | `backend/app.py`, `run.py` |
| Member 2 | ________________ | ________________ | Frontend UI | `frontend/templates/index.html` (HTML + CSS) |
| Member 3 | ________________ | ________________ | Frontend JS | `frontend/templates/index.html` (JavaScript) |
| Member 4 | ________________ | ________________ | Config & Docs | `config.py`, `scheduler.py`, `README.md` |

**Project Guide:** Ms. Ishita Tandon — Assistant Professor, Data & Infrastructure (SoCS), IILM University

---

## Features

| Feature | Description |
|---------|-------------|
| Dashboard | Live stats — total backups, today's count, last backup time |
| Manual Backup | Single on-demand commit with custom message |
| Auto Watch | Background watcher that auto-commits on any file change |
| Backup History | Full log of all backup commits with hashes and timestamps |
| Restore | Roll back any directory to any previous backup state |
| File Status | Live Git status showing modified / added / deleted files |

---

## Project Structure

```
GitVault/
├── run.py                        ← Start the app from here
├── config.py                     ← Per-directory settings manager
├── scheduler.py                  ← OS-level cron/Task Scheduler helper
├── README.md                     ← This file
├── backend/
│   └── app.py                    ← Flask REST API (10 endpoints)
└── frontend/
    └── templates/
        └── index.html            ← Complete dashboard (HTML + CSS + JS)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ + Flask |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Storage | Git (via Python subprocess module) |
| API Style | REST API (JSON) |
| External APIs | None |

---

## Installation & Run

### Requirements
- Python 3.10+
- Git 2.x (must be installed and in PATH)

### Steps

```bash
# Step 1 — Install Flask
pip install flask

# Step 2 — Run the app
python run.py

# Step 3 — Open in browser
# Go to: http://localhost:5000
```

---

## How to Use

1. Enter any folder path in the **top bar** and click **LOAD**
2. **Manual Backup** — go to Manual Backup → click Create Backup
3. **Auto Watch** — go to Auto Watch → set interval → Start Watching
4. **History** — view all past backups with timestamps
5. **Restore** — click any hash in History → confirm → restore

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/init` | POST | Initialize Git repo in a folder |
| `/api/backup` | POST | Create a manual backup commit |
| `/api/watch/start` | POST | Start auto-watch background thread |
| `/api/watch/stop` | POST | Stop auto-watch |
| `/api/watch/status` | POST | Get current watch status |
| `/api/log` | POST | Get backup commit history |
| `/api/status` | POST | Get Git status of directory |
| `/api/stats` | POST | Get backup statistics |
| `/api/restore` | POST | Restore to a specific commit |
| `/api/restore/latest` | POST | Return to latest backup |

---

## Version Control — CSE2480

This project uses Git and GitHub as required by the course guidelines.
Each member has this project on their individual GitHub profile.
