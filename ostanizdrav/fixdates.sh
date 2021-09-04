#!/bin/bash
set -e

#note: use gsed on MacOS instead of sed
sed -i'' -e 's/^[1-9]\./0&/g;' "$1"
