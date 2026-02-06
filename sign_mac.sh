#!/usr/bin/env bash
set -euo pipefail

APP_PATH="${1:-dist/WealthPulse.app}"
DMG_PATH="${2:-dist/WealthPulse.dmg}"

if [ ! -d "$APP_PATH" ]; then
  echo "App bundle not found at $APP_PATH"
  exit 1
fi

if [ ! -f "$DMG_PATH" ]; then
  echo "DMG not found at $DMG_PATH (build first with build_mac.sh)"
  exit 1
fi

if [ -z "${DEVELOPER_ID_APP:-}" ]; then
  echo "Set DEVELOPER_ID_APP to your Developer ID Application certificate name."
  exit 1
fi

if [ -z "${APPLE_ID:-}" ] || [ -z "${APPLE_TEAM_ID:-}" ] || [ -z "${APPLE_APP_PASSWORD:-}" ]; then
  echo "Set APPLE_ID, APPLE_TEAM_ID, and APPLE_APP_PASSWORD for notarization."
  exit 1
fi

echo "Signing app..."
codesign --deep --force --options runtime --sign "$DEVELOPER_ID_APP" "$APP_PATH"
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

echo "Submitting for notarization..."
xcrun notarytool submit "$DMG_PATH" \
  --apple-id "$APPLE_ID" \
  --team-id "$APPLE_TEAM_ID" \
  --password "$APPLE_APP_PASSWORD" \
  --wait

echo "Stapling notarization..."
xcrun stapler staple "$DMG_PATH"

echo "Done. Signed and notarized DMG: $DMG_PATH"
