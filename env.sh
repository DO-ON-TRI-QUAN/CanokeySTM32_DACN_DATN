#!/bin/bash
# Locate the compiler, CMake and Ninja that STM32CubeIDE installs, and put them
# on PATH for the current shell.
#
# Usage, from the repository root, in Git Bash:
#     source ./env.sh
#
# Run it once per terminal. It searches instead of hard-coding paths, so it
# keeps working after a CubeIDE update and on a different machine.

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  echo "ERROR: run this with 'source ./env.sh', not './env.sh'."
  echo "Without 'source' the settings are lost when the script ends."
  exit 1
fi

_ck_find_plugins() {
  local p
  for p in \
      /c/ST/STM32CubeIDE*/STM32CubeIDE/plugins \
      "/c/Program Files/STMicroelectronics/STM32CubeIDE"*/STM32CubeIDE/plugins \
      "/c/Program Files (x86)/STMicroelectronics/STM32CubeIDE"*/STM32CubeIDE/plugins \
      "$HOME"/ST/STM32CubeIDE*/STM32CubeIDE/plugins ; do
    [ -d "$p" ] && { echo "$p"; return 0; }
  done
  return 1
}

_ck_dir_of() {
  # $1 = plugins root, $2 = executable name
  local hit
  hit=$(find "$1" -maxdepth 5 -name "$2" 2>/dev/null | head -1)
  [ -n "$hit" ] && dirname "$hit"
}

CK_PLUGINS="${CK_PLUGINS:-$(_ck_find_plugins)}"

if [ -z "$CK_PLUGINS" ]; then
  echo "ERROR: could not find the STM32CubeIDE plugins folder."
  echo "Locate it yourself with:"
  echo "    find /c -maxdepth 3 -type d -name STM32CubeIDE"
  echo "then re-run as:"
  echo "    CK_PLUGINS=/c/<path>/STM32CubeIDE/plugins source ./env.sh"
  return 1
fi

CK_GCC_BIN=$(_ck_dir_of   "$CK_PLUGINS" arm-none-eabi-gcc.exe)
CK_CMAKE_BIN=$(_ck_dir_of "$CK_PLUGINS" cmake.exe)
CK_NINJA_BIN=$(_ck_dir_of "$CK_PLUGINS" ninja.exe)

_ck_missing=0
for _v in CK_GCC_BIN CK_CMAKE_BIN CK_NINJA_BIN ; do
  if [ -z "${!_v}" ]; then
    echo "ERROR: not found in $CK_PLUGINS -> $_v"
    _ck_missing=1
  fi
done
unset _v

if [ "$_ck_missing" = "1" ]; then
  echo "Install the missing component through the STM32CubeIDE installer,"
  echo "or install it separately and add it to PATH by hand."
  unset _ck_missing
  return 1
fi
unset _ck_missing

# Do not add the same folders twice if this file is sourced again.
case ":$PATH:" in
  *":$CK_GCC_BIN:"*) ;;
  *) export PATH="$CK_GCC_BIN:$CK_CMAKE_BIN:$CK_NINJA_BIN:$PATH" ;;
esac

# CMake needs the Windows form of the path (C:/... with forward slashes).
export CROSS_COMPILE_BIN="$(cygpath -m "$CK_GCC_BIN")"
export CUBE_BIN="$CROSS_COMPILE_BIN"   # older name, kept for the build guide

echo "STM32CubeIDE tools ready:"
echo "  gcc    $(arm-none-eabi-gcc --version 2>/dev/null | head -1)"
echo "  cmake  $(cmake --version 2>/dev/null | head -1)"
echo "  ninja  $(ninja --version 2>/dev/null)"
echo "  CUBE_BIN=$CUBE_BIN"
