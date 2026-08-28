#!/usr/bin/env bash
# Bundle RELAY submission files for upload via confirmation-email portal.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/RELAY_Submission_30Aug.zip"
STAGING="$ROOT/.submission_staging"

rm -rf "$STAGING"
mkdir -p "$STAGING"

copy() {
  local src="$1"
  local dest="$2"
  if [[ -f "$src" ]]; then
    cp "$src" "$STAGING/$dest"
    echo "  + $dest"
  else
    echo "  ! missing: $src"
    MISSING=1
  fi
}

MISSING=0
echo "Packaging RELAY submission..."

copy "$ROOT/RELAY_Presentation.pptx" "RELAY_Presentation.pptx"
copy "$ROOT/ARCHITECTURE.pdf" "ARCHITECTURE.pdf"
copy "$ROOT/ARCHITECTURE.md" "ARCHITECTURE.md"
copy "$ROOT/RELAY_Demo_PSA_CodeSprint.mp4" "RELAY_Demo_PSA_CodeSprint.mp4"

# Optional PDF export of slides (if user created it)
if [[ -f "$ROOT/RELAY_Presentation.pdf" ]]; then
  copy "$ROOT/RELAY_Presentation.pdf" "RELAY_Presentation.pdf"
fi

rm -f "$OUT"
(cd "$STAGING" && zip -q -r "$OUT" .)
rm -rf "$STAGING"

echo ""
echo "Created: $OUT"
if [[ "$MISSING" -eq 1 ]]; then
  echo ""
  echo "Note: some files were missing (usually the demo video)."
  echo "Record video per DEMO_VIDEO_SCRIPT.md, then re-run this script."
fi
