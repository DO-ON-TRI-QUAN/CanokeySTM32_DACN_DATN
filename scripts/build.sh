#!/bin/bash
# Usage (Git Bash): ./scripts/build.sh [--dumb] [--clean]

set -e

cd "$(dirname "${BASH_SOURCE[0]}")/.."
REPO_ROOT="$(pwd)"

PRESET=release
CLEAN=0
for arg in "$@"; do
  case "$arg" in
    --dumb)
      PRESET=dumb
      echo "WARNING: DUMB_DONGLE build. User-presence checks are disabled." \
           "Development only." >&2
      ;;
    --clean) CLEAN=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

BUILD_DIR="$REPO_ROOT/build/$PRESET"
PATCHED="$REPO_ROOT/canokey-core/canokey-crypto/patched"
PATCHED_ECP="$PATCHED/mbedtls/include/mbedtls/ecp.h"

echo "== 1/4  Locating STM32CubeIDE tools"
source ./scripts/env.sh

if [ "$CLEAN" = "1" ]; then
  echo "== Removing $BUILD_DIR"
  rm -rf "$BUILD_DIR"
fi

if [ ! -f "$BUILD_DIR/CMakeCache.txt" ]; then
  echo "== 2/4  Configuring preset '$PRESET'"
  # Patch fails on an already patched copy.
  rm -rf "$PATCHED"
  cmake --preset "$PRESET"

  echo "== 3/4  Verifying the mbedtls Ed25519 patch"
  if ! grep -q MBEDTLS_ECP_DP_ED25519 "$PATCHED_ECP" 2>/dev/null; then
    echo "ERROR: Ed25519 patch did not apply to mbedtls. Do not use this build." >&2
    echo "Check that GNU patch is on PATH: patch --version" >&2
    exit 1
  fi
  echo "OK - Ed25519 support present in patched mbedtls."
else
  echo "== 2/4  Configure skipped, cache exists. Use --clean to reconfigure."
  echo "== 3/4  Patch check skipped"
fi

echo "== 4/4  Building"
cmake --build --preset "$PRESET"

cd "$BUILD_DIR"
echo
ls -l canokey canokey.bin canokey.hex
arm-none-eabi-size canokey
echo "Linker limits: 194560 bytes Flash (text + data), 65536 bytes SRAM."
echo "Outputs in $BUILD_DIR"
