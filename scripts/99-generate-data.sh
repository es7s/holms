#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2024 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

__main() {
  local data_path=$(realpath "${1:-./misc}")

  ./run run <"$data_path/unicode_all_nolf.bin" -rfnumber,char,block,cat,name  | tee /dev/stderr \
    >"$data_path/unicode_chart.txt" \
    2> >(sed -Ee 1~100!d | tr $'\n' $'\r' >&2)
  sed "$data_path/unicode_chart.txt" -Ee $'s/\u200e//' -i
  rm "$data_path/unicode_chart.zip"
  zip -r "$data_path/unicode_chart.zip" "$data_path/unicode_chart.txt"
}


__main "$@"
