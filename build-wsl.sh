#!/usr/bin/env bash
# WSL build wrapper for canokey.bin using plain CMake + Make.
#
# Usage:
#   ./build-wsl.sh                  # default build, all features
#   ./build-wsl.sh --dumb           # DUMB_DONGLE build (user presence DISABLED)
#   ./build-wsl.sh --clean          # wipe that variant's build dir first
#   ./build-wsl.sh --dumb --clean   # flags can be combined
#
# Optional: TOOLCHAIN=/path/to/toolchain/bin/arm-none-eabi- ./build-wsl.sh

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

BUILD_DIR=build-wsl
EXTRA_CMAKE_ARGS=()
CLEAN=0

for arg in "$@"; do
  case "$arg" in
    --dumb)
      BUILD_DIR=build-wsl-dumb
      EXTRA_CMAKE_ARGS+=(-DENABLE_DUMB_DONGLE=ON)
      echo "WARNING: DUMB_DONGLE build. User-presence checks are disabled." \
           "Development only." >&2
      ;;
    --clean) CLEAN=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

TOOLCHAIN="${TOOLCHAIN:-arm-none-eabi-}"   # bare prefix = compiler is on PATH
PATCHED=canokey-core/canokey-crypto/patched

if ! command -v "${TOOLCHAIN}gcc" >/dev/null; then
  echo "ERROR: ${TOOLCHAIN}gcc not found. Install gcc-arm-none-eabi or set TOOLCHAIN." >&2
  exit 1
fi

if [[ $CLEAN -eq 1 ]]; then
  rm -rf "$BUILD_DIR"
fi

# Configure only when needed
if [[ ! -f "$BUILD_DIR/CMakeCache.txt" ]]; then
  # The mbedtls 'patched' copy must be removed before every configure,
  # otherwise the Ed25519 patch fails silently.
  rm -rf "$PATCHED"

  mkdir -p "$BUILD_DIR"
  (cd "$BUILD_DIR" && cmake \
      -DCROSS_COMPILE="$TOOLCHAIN" \
      -DCMAKE_TOOLCHAIN_FILE=../toolchain.cmake \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      ${EXTRA_CMAKE_ARGS[@]+"${EXTRA_CMAKE_ARGS[@]}"} \
      ..)

  # Only applies to the branch that patches mbedtls
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