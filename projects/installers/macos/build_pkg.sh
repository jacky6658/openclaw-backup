#!/bin/bash
set -euo pipefail

# Build a minimal macOS PKG that runs postinstall.
# NOTE: For real distribution, you should sign + notarize.

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_DIR="$ROOT_DIR/pkg"
SCRIPTS_DIR="$PKG_DIR/scripts"
OUT_DIR="$ROOT_DIR/dist"

mkdir -p "$OUT_DIR"
chmod +x "$SCRIPTS_DIR/postinstall"

IDENTIFIER="ai.openclaw.installer"
VERSION="0.1.0"
PKG_NAME="OpenClaw-Installer-macOS-${VERSION}.pkg"

EMPTY_ROOT="$ROOT_DIR/pkg/empty-root"
mkdir -p "$EMPTY_ROOT"

pkgbuild \
  --root "$EMPTY_ROOT" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --scripts "$SCRIPTS_DIR" \
  --install-location "/" \
  "$OUT_DIR/$PKG_NAME"

echo "Built: $OUT_DIR/$PKG_NAME"
