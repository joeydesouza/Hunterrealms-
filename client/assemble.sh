#!/usr/bin/env bash
# Overlay Hunter Realms files onto an OTClient checkout:
#   assemble.sh <otclient dir> <generated assets dir> <login url> <login port>
#   e.g. assemble.sh otclient build/assets http://play.hunterrealms.com/login 80
set -euo pipefail
OTC=$1; ASSETS=$2; URL=$3; PORT=$4
HERE=$(cd "$(dirname "$0")" && pwd)
cp -r "$HERE/overlay/." "$OTC/"
sed -i "s#HUNTER_LOGIN_URL#$URL#; s#HUNTER_LOGIN_PORT#$PORT#" "$OTC/init.lua"
rm -rf "$OTC/data/things" && mkdir -p "$OTC/data/things/1525"
cp "$ASSETS"/* "$OTC/data/things/1525/"
echo "client overlay applied to $OTC (login $URL port $PORT)"
