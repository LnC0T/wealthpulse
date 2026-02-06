#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3.10+ first."
  exit 1
fi

echo "Creating venv..."
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source ".venv/bin/activate"
python -m pip install --upgrade pip

echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
  python -m pip install -r requirements.txt
else
  python -m pip install streamlit yfinance pandas requests plotly pillow
fi
python -m pip install pyinstaller

echo "Cleaning previous builds..."
rm -rf dist build

ADD_DATA_ARGS=()
if [ -f "wealth_tracker.py" ]; then
  ADD_DATA_ARGS+=(--add-data "wealth_tracker.py:.")
fi
if [ -f "supabase_community_schema.sql" ]; then
  ADD_DATA_ARGS+=(--add-data "supabase_community_schema.sql:.")
fi
if [ -d "assets" ]; then
  ADD_DATA_ARGS+=(--add-data "assets:assets")
fi

echo "Building macOS app bundle..."
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "WealthPulse" \
  --collect-all "streamlit" \
  "${ADD_DATA_ARGS[@]}" \
  "mac_launcher.py"

APP_PATH="dist/WealthPulse.app"
DMG_PATH="dist/WealthPulse.dmg"
if [ -d "$APP_PATH" ]; then
  echo "Creating DMG..."
  rm -f "$DMG_PATH"
  hdiutil create -volname "WealthPulse" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"
fi

echo ""
echo "Build complete."
echo "App bundle: dist/WealthPulse.app"
if [ -f "$DMG_PATH" ]; then
  echo "Installer DMG: $DMG_PATH"
fi
