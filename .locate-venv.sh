#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/h0lmes
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

__main() {
  PATHS=(
    "./.hatch/dev/bin"
    "./venv/bin"
  )
  for file in "${PATHS[@]/%//python}" ; do
      [[ -x $file ]] && echo "$file" && return 0
  done
  return 1
}

__main "$@"
