#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
key_dir=${FAMILJEHEM_SIGNING_DIR:-../.private}
export YUVOMI_KEYSTORE_PATH="$(realpath "$key_dir/familjehem.jks")"
export YUVOMI_KEYSTORE_PASSWORD="$(cat "$key_dir/signing-password")"
export YUVOMI_KEY_PASSWORD="$YUVOMI_KEYSTORE_PASSWORD"
export YUVOMI_KEY_ALIAS=familjehem
exec ./gradlew --no-daemon assembleRelease -Pyuvomi.versionName=0.1.0 -Pyuvomi.versionCode=1 --max-workers=1
