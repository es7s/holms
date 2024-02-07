#!/bin/sh

VENV_USER_PATH="$HOME/.es7s/venv/holms"
ES7S_BIN_PATH="$HOME/.es7s/bin"

set -e

mkdir -p "$VENV_USER_PATH"
python -m pip install --upgrade virtualenv
python -m venv --upgrade-deps "$VENV_USER_PATH"
"${VENV_USER_PATH}/bin/pip" install -U .

[ -e "$ES7S_BIN_PATH/holms" ] || ln -s "${VENV_USER_PATH}/bin/holms" "$ES7S_BIN_PATH/holms"
"$ES7S_BIN_PATH/holms" version

case ":$PATH:" in
  *:"$ES7S_BIN_PATH":*) ;;
  *) echo "Add this to your PATH to invoke the app directly:"
     printf "  '%s'\n" "$ES7S_BIN_PATH"
     return 1
     ;;
esac
