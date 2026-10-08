#!/usr/bin/env bash
# Regenerate every derived file from source art + tables.
#   tools/build_all.sh <crawl-tiles release dir or "-" to keep assets/art> [out=build]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT"
TILES=${1:--}; OUT=${2:-build}
python3 -m grpc_tools.protoc -Itools/assetc --python_out=tools/assetc tools/assetc/appearances.proto
if [ "$TILES" != "-" ]; then rm -rf assets/art; python3 tools/assetc/make_starter.py "$TILES" .; fi
python3 tools/assetc/assetc.py assets/manifest.json "$OUT/assets"
python3 tools/assetc/verify.py "$OUT/assets"
python3 tools/mapgen/items_xml.py assets/manifest.json "$OUT/items.xml"
python3 tools/mapgen/monsters.py server/data-hunterrealms/monster
python3 tools/mapgen/world.py "$OUT/world"
echo "all generated into $OUT/"
