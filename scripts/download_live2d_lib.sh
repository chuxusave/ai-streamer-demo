#!/bin/bash
# 下载 pixi-live2d-display 库到本地

set -e

LIB_DIR="static/libs/pixi-live2d-display"
VERSION="0.4.0"

echo "📦 Downloading pixi-live2d-display@${VERSION}..."

# Create directory
mkdir -p "$LIB_DIR"

# Try to download from unpkg
echo "Trying unpkg..."
if curl -f -o "${LIB_DIR}/index.umd.js" "https://unpkg.com/pixi-live2d-display@${VERSION}/dist/index.umd.js" 2>/dev/null; then
    echo "✅ Downloaded from unpkg"
    exit 0
fi

# Try jsdelivr
echo "Trying jsdelivr..."
if curl -f -o "${LIB_DIR}/index.umd.js" "https://cdn.jsdelivr.net/npm/pixi-live2d-display@${VERSION}/dist/index.umd.js" 2>/dev/null; then
    echo "✅ Downloaded from jsdelivr"
    exit 0
fi

echo "❌ Failed to download from CDN"
echo "Please try manually:"
echo "  curl -o ${LIB_DIR}/index.umd.js https://unpkg.com/pixi-live2d-display@${VERSION}/dist/index.umd.js"
exit 1
