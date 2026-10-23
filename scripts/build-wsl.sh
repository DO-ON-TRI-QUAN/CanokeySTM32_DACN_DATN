#!/usr/bin/env bash
# Usage (WSL): ./scripts/build-wsl.sh [--dumb] [--clean]
# Optional: TOOLCHAIN=/path/to/bin/arm-none-eabi- ./scripts/build-wsl.sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
REPO_ROOT="$(pwd)"

BUILD_DIR=build/wsl-release
EXTRA_CMAKE_ARGS=()
CLEAN=0

for arg in "$@"; do
  case "$arg" in
    --dumb)
      BUILD_DIR=build/wsl-dumb
      EXTRA_CMAKE_ARGS+=(-DENABLE_DUMB_DONGLE=ON)
      echo "WARNING: DUMB_DONGLE build. User-presence checks are disabled." \
           "Development only." >&2
      ;;
    --clean) CLEAN=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

TOOLCHAIN="${TOOLCHAIN:-arm-none-eabi-}"
PATCHED=canokey-core/canokey-crypto/patched

if ! command -v "${TOOLCHAIN}gcc" >/dev/null; then
  echo "ERROR: ${TOOLCHAIN}gcc not found. Install gcc-arm-none-eabi or set TOOLCHAIN." >&2
  exit 1
fi

if [[ $CLEAN -eq 1 ]]; then
  rm -rf "$BUILD_DIR"
fi

if [[ ! -f "$BUILD_DIR/CMakeCache.txt" ]]; then
  # Patch fails on an already patched copy.
  rm -rf "$PATCHED"

  cmake -S "$REPO_ROOT" -B "$BUILD_DIR" \
      -DCROSS_COMPILE="$TOOLCHAIN" \
      -DCMAKE_TOOLCHAIN_FILE="$REPO_ROOT/toolchain.cmake" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      ${EXTRA_CMAKE_ARGS[@]+"${EXTRA_CMAKE_ARGS[@]}"}

  ECP="$PATCHED/mbedtls/include/mbedtls/ecp.h"
  if [[ -d "$PATCHED" ]]; then
    if ! grep -q MBEDTLS_ECP_DP_ED25519 "$ECP" 2>/dev/null; then
      echo "ERROR: Ed25519 patch did not apply to mbedtls. Is GNU patch installed?" >&2
      exit 1
    fi
    echo "OK - Ed25519 support present in patched mbedtls."
  fi
fi

make -C "$BUILD_DIR" canokey.bin -j"$(nproc)"

echo
ls -l "$BUILD_DIR"/canokey.bin
"${TOOLCHAIN}size" "$BUILD_DIR"/canokey 2>/dev/null || true
