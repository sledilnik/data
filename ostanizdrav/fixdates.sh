#!/bin/bash
set -e

sed -i '' -e 's/^[1-9]\./0&/g;' "$1"
