#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2024 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

__main() {
  local examples_path=$(realpath "${1:-./misc}")
  local help_text_path="$examples_path/help.txt"
  __help_text_size() { stat "$help_text_path" --format="%s" ; }

  local size_before=$(__help_text_size)
  ./run run --help >"$help_text_path.tmp"
  local opt_start=$(grep <"$help_text_path.tmp" -Ee '^\s*Options:' -m1 -no | cut -d: -f1)
  cut -f${opt_start}- -d$'\n' < "$help_text_path.tmp" > "$help_text_path"
  rm "$help_text_path.tmp"
  printf "Updated '%s': %d -> %d bytes\n" "$help_text_path" "$size_before" "$(__help_text_size)"
}


__main "$@"
