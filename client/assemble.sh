#!/usr/bin/env bash
# Overlay Hunter Realms files onto an OTClient checkout:
#   assemble.sh <otclient dir> <generated assets dir> <login url> <login port>
#   e.g. assemble.sh otclient build/assets http://play.hunterrealms.com/login 80
set -euo pipefail
OTC=$1; ASSETS=$2; URL=$3; PORT=$4
HERE=$(cd "$(dirname "$0")" && pwd)
cp -r "$HERE/overlay/." "$OTC/"
sed -i "s#HUNTER_LOGIN_URL#$URL#; s#HUNTER_LOGIN_PORT#$PORT#" "$OTC/init.lua"
# register our mods with the mod loader
grep -q "hr_assistant" "$OTC/mods/client_mods/mods.otmod" || \
  sed -i 's/^    - game_bot$/    - game_bot\n    - hr_assistant/' "$OTC/mods/client_mods/mods.otmod"
rm -rf "$OTC/data/things" && mkdir -p "$OTC/data/things/1525"
cp "$ASSETS"/* "$OTC/data/things/1525/"
echo "client overlay applied to $OTC (login $URL port $PORT)"

# Android branding (only when the checkout has the android project)
if [ -d "$OTC/android/app" ]; then
  sed -i 's/applicationId = "com.github.otclient"/applicationId = "com.hunterrealms.game"/' "$OTC/android/app/build.gradle.kts"
  sed -i 's#<string name="app_name">otclient</string>#<string name="app_name">Hunter Realms</string>#' \
    "$OTC/android/app/src/main/res/values/strings.xml"
  echo "android branding applied"
fi
