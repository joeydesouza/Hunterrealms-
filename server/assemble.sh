#!/usr/bin/env bash
# Assemble a runnable server folder:
#   assemble.sh <canary checkout> <canary binary> <generated assets dir> <out dir>
# Layers: canary core data -> our core overrides -> our datapack + generated assets.
set -euo pipefail
CANARY=$1; BIN=$2; GEN=$3; OUT=$4
HERE=$(cd "$(dirname "$0")" && pwd)
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$BIN" "$OUT/canary"
cp -r "$CANARY/data" "$OUT/data"
cp "$CANARY/key.pem" "$OUT/"
cp -r "$HERE/core-overrides/." "$OUT/data/"
cp -r "$HERE/data-hunterrealms" "$OUT/"
cp "$HERE/config.lua" "$OUT/"
cp "$GEN/assets/appearances.dat" "$OUT/data/items/appearances.dat"
cp "$GEN/items.xml" "$OUT/data/items/items.xml"
cp "$GEN"/world/* "$OUT/data-hunterrealms/world/"
echo "server assembled in $OUT"
