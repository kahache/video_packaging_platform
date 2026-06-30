#!/bin/bash
# Download a small public sample .mp4 into tests/TEST_VIDEOS/ for the E2E tests.
# Skips the download if a sample is already present.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/../TEST_VIDEOS"
mkdir -p "$DEST"

# A small (~2 MB) H.264/AAC clip with a real video track. Override with $E2E_URL.
URL="${E2E_URL:-http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4}"
NAME="$(basename "$URL")"

if ls "$DEST"/*.mp4 >/dev/null 2>&1; then
    echo "Sample video already present:"
    ls -lh "$DEST"/*.mp4
    exit 0
fi

echo "Downloading $URL -> $DEST/$NAME"
if command -v wget >/dev/null 2>&1; then
    wget -O "$DEST/$NAME" "$URL"
elif command -v curl >/dev/null 2>&1; then
    curl -L -o "$DEST/$NAME" "$URL"
else
    echo "ERROR: need wget or curl to download the sample." >&2
    exit 1
fi

echo "Done:"
ls -lh "$DEST/$NAME"
