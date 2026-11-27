#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Creating virtual environment (.venv)..."
python3 -m venv .venv

echo "[2/4] Installing dependencies..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip install --no-deps -e .

echo "[3/4] Checking ffmpeg..."
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "WARNING: ffmpeg not found in PATH. Install it (brew install ffmpeg / apt install ffmpeg) to enable YouTube clip trimming, scene-change detection, and keyframe extraction."
else
  echo "ffmpeg detected."
fi

echo "[4/4] Running test suite..."
./.venv/bin/pytest -v

echo ""
echo "Setup complete. Try: ./.venv/bin/python -m app_teardown.cli discover \"hypercasual runner\" --limit 5"
