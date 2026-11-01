#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$task_root/Website"
export PYTHONUTF8=1
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements.txt
printf '\nTechVerse: http://127.0.0.1:5000 — Ctrl+C to stop.\n\n'
exec .venv/bin/python run.py
