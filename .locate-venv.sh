#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

__main() {
  srcpath=$(dirname "$(realpath "$BASH_SOURCE[0]/")")
  PATHS=(
    ".hatch/dev/bin"
    "venv/bin"
  )
  for file in "$srcpath/${PATHS[@]/%//python}" ; do
      [[ -x $file ]] && echo "$file" && return 0
  done
  return 1
}

__main "$@"
