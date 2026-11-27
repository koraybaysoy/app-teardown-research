# One-step setup for Windows (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "[1/4] Creating virtual environment (.venv)..."
python -m venv .venv

Write-Host "[2/4] Installing dependencies..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .

Write-Host "[3/4] Checking ffmpeg..."
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Warning "ffmpeg not found in PATH. Install it (e.g. 'winget install Gyan.FFmpeg') to enable YouTube clip trimming, scene-change detection, and keyframe extraction."
} else {
    Write-Host "ffmpeg detected."
}

Write-Host "[4/4] Running test suite..."
.\.venv\Scripts\pytest.exe -v

Write-Host "`nSetup complete. Try: .\.venv\Scripts\python.exe -m app_teardown.cli discover `"hypercasual runner`" --limit 5"
