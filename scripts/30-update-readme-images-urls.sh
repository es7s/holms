#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

__main() {
  local readme_path=$(realpath "${1:-./README.md}")
  local urls_path=$(realpath "${2:-./scripts/readme-images-urls.md}")
  __readme_size() { stat "$readme_path" --format="%s" ; }

  local size_before=$(__readme_size)
  while read -r line ; do
    local imgname="$(sed -Ee "s/.+\[([^]]+)\].+/\1/" <<< "$line")"
    local imgurl="$(sed -Ee "s/.+\(([^)]+)\)/\1/" <<< "$line")"
    sed -i -Ee "s|(<img alt=\"$imgname\".+src=\")([^\"]+)|\1$imgurl|1" "$readme_path"
  done < "$urls_path"
  printf "Updated '%s': %d -> %d bytes\n" "$readme_path" "$size_before" "$(__readme_size)"
}


__main "$@"
