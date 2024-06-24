#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------
declare -ir PP=15

declare -ir CHAR_W_PX=9
declare -ir CHAR_H_PX=21
declare -ir MIN_RESULT_W_PX=500
declare -ir MAX_RESULT_H_PX=1000
declare -ir OFFSET_X_PX=0
declare -ir OFFSET_Y_PX=0
declare -ir PADDING_X_CH=1
# values are adjusted for:
# -----------------------------------------
# TERMINAL APP  GNOME Terminal / Terminator
#    TEXT FONT  Iose7ka Terminal Medium 12
#  WINDOW SIZE  fullscreen 1080p
# -----------------------------------------

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
  echo "USAGE: $__SELF [-a] [-y] [OUTPUT_DIR] [EXEC_DIR]"
  echo
  echo "  Render readme images, place into OUTPUT_DIR. If specified,"
  echo "  use EXEC_DIR as custom path to 'holms'. Both can be provided"
  echo "  in a format relative to current working directory."
  echo
  echo "Suggested invocation (non-interactive):"
  echo "  make pre-build"
  echo "Suggested invocation (manual control):"
  echo "  ./scripts/make-readme-images.sh ./misc"
  echo
  echo "OPTIONS"
  echo "  -a, --all    Do not skip already existing artifacts."
  echo "  -y, --yes    Write artifacts without user confirmation."
}
__holms() {
    if command -v gnome-terminal 2>/dev/null && [[ -z $ES7S_X11_SHELL ]] ; then
      local srcpath=$(realpath "${BASH_SOURCE[0]}")
      ES7S_X11_SHELL=$$ es7s exec open-terminal . -- \
          --window --full-screen -- \
          bash -i "$srcpath" "$@"
      return
    fi

    local OPT_ALL=
    local OPT_YES=

    while getopts ay-: OPT; do
        if [ "$OPT" = "-" ]; then
            OPT="${OPTARG%%=*}"
            OPTARG="${OPTARG#$OPT}"
            OPTARG="${OPTARG#=}"
        fi
        # shellcheck disable=SC2214
        case "$OPT" in
                 a|all) OPT_ALL=true ;;
                 y|yes) OPT_YES=true ;;
                  help) __help && return 0 ;;
                 ??*|?) echo "Invalid option -${OPTARG:-"-"$OPT}" && __help && return 0 ;;
        esac
    done
    shift $((OPTIND-1))

    # shellcheck disable=SC2086
    function invoke() {
      # args: opts [file] [input] [precmd preopts...]
      local opts="-b $1" file="${2:--}" input="${3:-}"
      local hopts=" $1${1:+ }"
      local hcmd="run"

      local hfile="$file"
      [[ $file =~ ^/ ]] && hfile="$(basename "$file")"

      [[ $hopts =~ -.*L ]] && opts="" && hopts="" && hcmd="legend" && hfile= && file=
      [[ $hopts =~ -.*F ]] && opts="" && hopts="" && hcmd="format" && hfile= && file=
      hopts="${hopts/-u /}"
      local hstart="holms $hcmd"
      local hend=" $hfile"

      if [[ -n $input ]] ; then
        hopts+=" -u"
#        hend+=$'\n'"$input"
        hend+=" <<<'$input'"$'\n '
      elif [[ -n "$4" ]] ; then
          if [[ -z "$ES7S_PADBOX_HEADER" ]] ; then
            hprecmd=("${@:4}")
            hstart="$(sed <<< "${hprecmd[@]@Q}" -Ee "s/'([^ !\\]*)'/\1/g; s|\.?/[^ ]+/([^/ ]+)|\1|g") |"$'\n'"  $hstart"
          else
            hstart="$ES7S_PADBOX_HEADER |"$'\n'"  $hstart"
          fi
          hend+=$'\n '
      else
        hend+=$'\n '
      fi
#      echo "${@:4}" | kolombos -d
      { [[ -n $input ]] && printf %s $input || "${@:4}" ; } |
        ES7S_PADBOX_BG_COLOR='' \
        ES7S_PADBOX_HEADER="${hstart}${hopts}${hend}" \
          padbox "${execpath:-holms}" -c $hcmd $file $opts
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
    function invoke_cut_seamless() {
      # shellcheck disable=SC2054
      local -a expr=(-e 1,2p)
      readarray -t params < <(cat)
      for param in "${params[@]}" ; do expr+=(-e "${param}"p) ; done
#      while IFS= read -r line; do expr+=(-e "${line}"p) ; done < <(cat)
      invoke "${@}" | sed -nE "${expr[@]}"
    }
    function invoke_limit() { ES7S_PADBOX_LINE_LIMIT=10 invoke "$@" ; }
    function p1() { invoke_simple '1₂³⅘↉⏨' ; }
    function p2() { invoke_simple 'aаͣāãâȧäåₐᵃａ' ; }
    function p3() { invoke_simple '%‰∞8᪲?¿‽⚠⚠️' ; }
    function p4() { invoke_simple '🌯👄🤡🎈🐳🐍' ; }
    function p5() { invoke_limit -m ~/phpstan.txt ; }
    function p6() { invoke "" "" "" sed ./tests/data/confusables.txt -Ee 's/^.|\t//g' -e 3620!d ; }
    function p7() { invoke "--format=char" "" "" sed ./tests/data/chars.txt -nEe '1,12p' ; }
    function p8() { invoke_limit -g ./tests/data/confusables.txt ; }
    function p9() { invoke_cut_seamless <<<337,368 -L ; }
#    function p9() {
      # 4,35 35,65 65,95 95,125 125,155 155,185 185,215 215,245 245,275 275,305 305,333
#      invoke_cut_seamless -L <<<4,35
#    }
    function p10() { ES7S_PADBOX_PAD_X=0 invoke_cut 22 "" -F  ; }
    function p11() { invoke_limit -gg ./tests/data/confusables.txt ; }
    function p12() { invoke_limit -ggg ./tests/data/confusables.txt ; }
    function p13() {
      local data="\x80\x90\x9f"
      echo "$(cat <<EOF
printf "$data" && python3 -c 'print("$data", end="")'
EOF
)" > /tmp/p13
    ES7S_PADBOX_HEADER="$(cat /tmp/p13)" _p13 bash /tmp/p13
    }
    function _p13() { invoke "--names --decimal --all" "" "" "$@" | sed -Ee '6s/$/\n/' ; }
#    function p14() { invoke ""  ./tests/data/specials ; }
    function p14() { invoke_cut_seamless <<<371,\$ -L ; }
    function p15() { invoke_limit -fchar ./tests/data/broken-utf8.txt ; }

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
        :
#        local fnum="${1:?}"
#        [[ $fnum == 13 ]] && echo 2 5
#        echo 2
    }
    function get_extra_strokes_px() {
        for h in $(get_extra_strokes "$@") ; do
          echo $(( h * CHAR_H_PX ))
        done
    }

    # shellcheck disable=SC2054,SC2206
    function pp() {
        # args: imgin imgout [header_hpx...]

        local -a cmds=()
        for h in ${*:3} ; do
          cmds+=(polygon 2,0,$h,100%,$h,1,0xaaaaaaaa,100)
        done

        cmds+=(
          to_rgba
          #fx_frame 0,100,0,100,0,0,255,255,255,255,1,100,100,100,255
          expand_x 15,0
          expand_y 15,0
          crop 0,15,100%,100%,0
          drop_shadow 5,5,2.5,0,0,0
          output "${2:?}"
          display_rgba
        )

        gmic "${1:?}" "${cmds[@]}"
    }

    local outdir=$(realpath "${1:-.}")
    local execpath=$(realpath "${2:-./run}")

    local tmpout=/tmp/pbc-out
    local tmpimg=/tmp/pbc.png
    local tmpimgpp=/tmp/pbcpp.png
    local promptyn=$'\x1b[m Save? \x1b[34m[y/N/^C]\x1b[94m>\x1b[m '

    [[ -d "$outdir" ]] || { echo "ERROR: Dir does not exist: ${outdir@Q}" && exit 1 ; }
    [[ -x "$execpath" ]] || execpath=

    export ES7S_PADBOX_PAD_Y=0
    export ES7S_PADBOX_PAD_X=$PADDING_X_CH
    export ES7S_PADBOX_NO_CLEAR=true
    export PAGER=

    for fn in $(seq $PP) ; do
        local imgout="$outdir/example$(printf %03d $fn).png"
        local txtout="$imgout.txt"
        local prompt=$(printf '\x1b[33m[\x1b[93;1m%2d\x1b[;33m/\x1b[1m%2d\x1b[;33m]\x1b[m' "$fn" $PP)

        if [[ ! $OPT_ALL ]] ; then
          # shellcheck disable=SC2046,SC2005
          [[ -f "$imgout" && -f "$txtout" ]] \
            && echo "$prompt Skipping existing: $(echo $(basename -a "$imgout" "$txtout"))" \
            && continue
        fi

        clear
        "p$fn" |& tee $tmpout

        sleep 0.5
        local dimensions=$(measure "$tmpout")
        scrot -o "$tmpimg" -a "$dimensions"  #-e 'xdg-open $f'

        # shellcheck disable=SC2046,SC2086
        pp "$tmpimg" "$tmpimgpp" $(get_extra_strokes_px $fn)

        if [[ ! $OPT_YES ]] ; then
          read -r -n1 -p"$prompt$promptyn" yn ; echo
        else yn=y ; fi
        if [[ $yn =~ [Yy] ]] ; then
            cp -v "$tmpimgpp" "$imgout"
            dcu < "$tmpout" > "$txtout"
            fstat "$imgout" "$txtout"
        fi
    done

    [[ -n "$ES7S_X11_SHELL" ]] && read -rn1 -p "Done. Press any key to exit"
}

checkdep holms
checkdep gmic
checkdep padbox es7s
(__holms "$@")
