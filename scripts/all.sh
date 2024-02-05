#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/holms
# (c) 2024 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

set -e

ARG_FORCE=
[[ $* =~ --force ]] && ARG_FORCE=true

./scripts/00-update-help-text.sh ./misc
./scripts/10-make-readme-images.sh ${ARG_FORCE:+-ay} ./misc
./scripts/20-substitute-readme-plain-text.py ./README.md ./misc
./scripts/30-update-readme-images-urls.sh ./README.md ./scripts/readme-images-urls.md
