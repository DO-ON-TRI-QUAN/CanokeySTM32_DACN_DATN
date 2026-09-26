#!/bin/bash
# Build canokey.bin from a clean state.
#
# Usage, in Git Bash, from anywhere:
#     ./build.sh
#
# Requires STM32CubeIDE to be installed. It provides the compiler, CMake and
# Ninja; env.sh finds them.

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"
REPO_ROOT="$(pwd)"

echo "=============================================="
echo " 1/5  Locating STM32CubeIDE tools"
echo "=============================================="
source ./env.sh

echo
echo "=============================================="
echo " 2/5  Cleaning previous build state"
echo "=============================================="
# 'patched' holds a patched copy of mbedtls. It MUST be removed before every
# configure, otherwise the build tries to patch already-patched files, the
# patch fails, and the failure is ignored.
rm -rf build
rm -rf canokey-core/canokey-crypto/patched
echo "removed: build/, canokey-core/canokey-crypto/patched/"

echo
echo "=============================================="
echo " 3/5  Configuring"
echo "=============================================="
# Settings live in CMakePresets.json.
#
# This script uses the 'cli-release' preset, which builds into build/.
# STM32CubeIDE uses the 'release' preset, which builds into release/.
# Same compiler and flags; separate directories, so the two never overwrite
# each other's files.
#
# The presets use the bare prefix "arm-none-eabi-" rather than a full path.
# env.sh above put the compiler on PATH, and CubeIDE does the same for its own
# builds, so the presets work on any machine with STM32CubeIDE installed.
cmake --preset cli-dumb

echo
echo "=============================================="
echo " 4/5  Verifying the mbedtls Ed25519 patch"
echo "=============================================="
PATCHED_ECP="$REPO_ROOT/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ecp.h"

if [ ! -f "$PATCHED_ECP" ]; then
  echo "ERROR: $PATCHED_ECP does not exist."
  echo "The mbedtls copy step did not run. Do not use this build."
  exit 1
fi

if ! grep -q MBEDTLS_ECP_DP_ED25519 "$PATCHED_ECP"; then
  echo "ERROR: the Ed25519 patch did NOT apply to mbedtls."
  echo
  echo "The firmware would still compile, and then fail at runtime whenever"
  echo "OpenPGP touches an Ed25519 key. Do not use this build."
  echo
  echo "Check that GNU patch is installed and on PATH:  patch --version"
  exit 1
fi
echo "OK - Ed25519 support is present in the patched mbedtls."

echo
echo "=============================================="
echo " 5/5  Building"
echo "=============================================="
cmake --build --preset cli-dumb

cd "$REPO_ROOT/build"

echo
echo "=============================================="
echo " Done"
echo "=============================================="
ls -l canokey canokey.bin canokey.hex
echo
echo "Size (Flash = text + data, RAM at startup = data + bss):"
arm-none-eabi-size canokey
echo
echo "Chip limits: 256 KiB Flash (262144 bytes), 64 KiB SRAM (65536 bytes)."
echo
echo "Outputs in $REPO_ROOT/build/ :"
echo "  canokey       ELF, for the debugger"
echo "  canokey.bin   raw binary, flash at 0x08000000"
echo "  canokey.hex   Intel HEX, address is inside the file"
