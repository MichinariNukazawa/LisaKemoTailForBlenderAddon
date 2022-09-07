#!/bin/bash
#
# Author: michinari.nukazawa@gmail.com
#

set -eu
set -o pipefail

trap 'echo "error:$0($LINENO) \"$BASH_COMMAND\" \"$@\""' ERR

rm -rf LisaKemoTailForBlenderAddon.zip
zip LisaKemoTailForBlenderAddon LisaKemoTailForBlenderAddon.py

