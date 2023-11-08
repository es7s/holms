#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------
declare -ir CHAR_W_PX=9
declare -ir CHAR_H_PX=21

function fstat() { stat -Lc $'%10s  %n' "$@" | es7s exec hilight - ; }
function min() { [[ $(( ${1:?} )) -lt $(( ${2:?} )) ]] && echo $1 || echo $2 ; }
function max() { [[ $(( ${1:?} )) -gt $(( ${2:?} )) ]] && echo $1 || echo $2 ; }
function dcu() { sed -Ee 's/\x1b\[[0-9;:]*[A-Za-z]//g; s/\xe2\x80\x8e//g'; }
function checkdep() {
  command -v "${1:?}" &>/dev/null && return
  echo "ERROR: ${2:-$1} not installed, unable to proceed"
  exit 1
}
function measure_width() {
  # reads stdin
  { while read -r line ; do
      wc <<< "$line" -m
    done < <(dcu) ;
  } | sort -nr | head -1 ;
}

# ------------------
__help() {
  __SELF="$(basename "$0" | sed -Ee 's/\..+$//')"
  echo "USAGE: $__SELF [OUTPUT_DIR]"
  echo
  echo "  Readme images renderer."
}
__holms() {
    local -ir MIN_RESULT_W_PX=500
    local -ir MAX_RESULT_H_PX=1000
    local -ir OFFSET_X_PX=0
    local -ir OFFSET_Y_PX=68
    local -ir PADDING_X_CH=1

    local -ir PP=14

    # shellcheck disable=SC2086
    function invoke() {
      # args: opts [file] [input] [precmd preopts...]
      local opts="-cSb $1" file="${2:--}" input="${3:-}"
      local hopts=" $1${1:+ }-S"
      local hstart="holms"

      local hfile="$file"
      [[ $file =~ ^/ ]] && hfile="$(basename "$file")"
      local hend=" $hfile"

      [[ $hopts =~ -.*L ]] && hopts=" -L" && hend=""
      hopts="${hopts/-u /}"

      if [[ -n $input ]] ; then
        hopts+=" -u" ; hend+=$'\n'"$input"
      elif [[ -n "$4" ]] ; then
        hprecmd=("${@:4}")
        hstart="$(sed <<< "${hprecmd[@]@Q}" -Ee "s/'([^ !\\]*)'/\1/g; s|\.?/[^ ]+/([^/ ]+)|\1|g") |"$'\n'"  $hstart"
      else
        hend+=$'\n '
      fi


      { [[ -n $input ]] && printf %s $input || "${@:4}" ; } |
        ES7S_PADBOX_HEADER="${hstart}${hopts}${hend}" padbox holms "$file" -cbS $opts
    }
    function invoke_simple() { invoke "" "" "${1:?}" ; }
    function invoke_cut() {
      local start="${1?}"
      local end="${2?}"

      local -a expr=(-e "${start:-1},${end:-$}p")
      [[ -n $start ]] && expr+=(-e "$((start - 1))s/.*/.../p")
      [[ -n $end ]] && expr+=(-e "$((end + 1))s/.*/.../p")

      invoke "${@:3}" | sed -nEe 1,2p "${expr[@]}"
    }
    function invoke_limit() { ES7S_PADBOX_LINE_LIMIT=10 invoke "$@" ; }
    function p1() { invoke_simple '1₂³⅘↉⏨' ; }
    function p2() { invoke_simple 'aаͣāãâȧäåₐᵃａ' ; }
    function p3() { invoke_simple '%‰∞8᪲?¿‽⚠⚠️' ; }
    function p4() { invoke_simple '🌯👄🤡🎈🐳🐍' ; }
    function p5() { invoke_limit -m ~/phpstan.txt ; }
    function p6() { invoke "" "" "" sed ./tests/data/confusables.txt -Ee 's/^.|\t//g' -e 3620!d ; }
    function p7() { invoke --format=char "" "" sed ./tests/data/chars.txt -nEe '150,159p' ; }
    function p8() { invoke_limit -g ./tests/data/confusables.txt ; }
    function p11() { invoke_limit -gg ./tests/data/confusables.txt ; }
    function p12() { invoke_limit -ggg ./tests/data/confusables.txt ; }
    function p9() { invoke_cut 36 "" -L  ; }
    function p10() { invoke_cut 20 33 -L  ; }
    function p13() { _p13 printf '\x80\x90\x9f' ; _p13 python -c 'print("\x80\x90\x9f", end="")' ; }
    function _p13() { invoke "-u --format=raw,number,char,type,name" "" "" "$@" ; }
    function p14() { invoke ""  ./tests/data/specials ; }

    function measure() {
      # arg: filepath
      local w_ch=$(measure_width < ${1:?})
      local h_ch=$(wc -l < ${1:?})
      echo "measured (ch): $w_ch $h_ch" >&2

      local result_w_px=$(max $MIN_RESULT_W_PX $(( CHAR_W_PX * (w_ch + 2*PADDING_X_CH) )) )
      local result_h_px=$(min $MAX_RESULT_H_PX $(( CHAR_H_PX * h_ch )) )
      echo "measured (px): $result_w_px $result_h_px" >&2

      echo "$OFFSET_X_PX,$OFFSET_Y_PX,$result_w_px,$result_h_px"
    }

    function get_extra_strokes() {
        local fnum="${1:?}"
        [[ $fnum == 13 ]] && echo 2 5 7
        echo 2
    }

    # shellcheck disable=SC2054,SC2206
    function pp() {
        # args: imgin imgout [header_hch...]

        local -a cmds=()
        for h in ${*:3} ; do
          local -i header_hpx=$(( h * CHAR_H_PX + 1 ))
          cmds+=(polygon 2,0,$header_hpx,100%,$header_hpx,1,66)
        done

        cmds+=(
          to_rgba
          fx_frame 0,100,0,100,0,0,255,255,255,255,1,100,100,100,255
          expand_x 15,0
          expand_y 15,0
          crop 0,15,100%,100%,0
          drop_shadow 5,5,2.5,0,0,0
          output "${2:?}"
          display_rgba
        )

        gmic "${1:?}" "${cmds[@]}"
    }

    local wd="${1:-.}"
    local tmpout=/tmp/pbc-out
    local tmpimg=/tmp/pbc.png
    local tmpimgpp=/tmp/pbcpp.png
    local promptyn=$'\x1b[m Save? \x1b[34m[y/N/^C]\x1b[94m>\x1b[m '

    [[ -n $wd ]] && { pushd "$wd" || exit 1 ; }

    export ES7S_PADBOX_PAD_Y=0
    export ES7S_PADBOX_PAD_X=$PADDING_X_CH
    export ES7S_PADBOX_NO_CLEAR=true
    export PAGER=

    for fn in $(seq $PP) ; do
        local imgout="./example$(printf %03d $fn).png"
        local txtout="$imgout.txt"
        local prompt=$(printf '\x1b[33m[\x1b[93;1m%2d\x1b[;33m/\x1b[1m%2d\x1b[;33m]\x1b[m' "$fn" $PP)

        # shellcheck disable=SC2046,SC2005
        [[ -f "$imgout" && -f "$txtout" ]] \
          && echo "$prompt Skipping existing: $(echo $(basename -a "$imgout" "$txtout"))" \
          && continue

        clear
        "p$fn" |& tee $tmpout

        sleep 0.5
        scrot -o "$tmpimg" -a "$(measure "$tmpout")"  #-e 'xdg-open $f'

        # shellcheck disable=SC2046,SC2086
        pp "$tmpimg" "$tmpimgpp" $(get_extra_strokes $fn)

        read -r -n1 -p"$prompt$promptyn" yn ; echo
        if [[ $yn =~ [Yy] ]] ; then
            cp -v "$tmpimgpp" "$imgout"
            dcu < "$tmpout" > "$txtout"
            fstat "$imgout" "$txtout"
        fi
    done

    [[ -n $wd ]] && { popd || exit 1 ; }
}

[[ ${*/ /s} =~ (^| )-{,2}h(elp)?( |$) ]] && __help && exit
checkdep holms
checkdep gmic
checkdep padbox es7s
(__holms "$@")
