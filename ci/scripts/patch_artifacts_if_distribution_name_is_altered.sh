#!/bin/bash
set -e
set -o pipefail

artifacts=$*
injection_string="Provides-Dist: appmap"
if [ -n "$artifacts" ] && [ -n "$DISTRIBUTION_NAME" ] && [ "$DISTRIBUTION_NAME" != "appmap" ]; then
  echo "Altered distribution name detected, injecting '$injection_string' into artifacts: $artifacts"
  for artifact in $artifacts ; do
    TMP=$(mktemp -d)
    ARTIFACT_PATH="$(realpath ${artifact})"
    if [[ $artifact == *.whl ]]; then
        unzip -q "$ARTIFACT_PATH" -d "$TMP"
        DISTINFO=$(find "$TMP" -type d -name "*.dist-info")
        echo "$injection_string" >> "$DISTINFO/METADATA"
        (cd "$TMP" && zip -qr "$ARTIFACT_PATH" .)
    else
        tar -xzf "$ARTIFACT_PATH" -C "$TMP"
        PKGDIR=$(find "$TMP" -maxdepth 1 -type d -name "*.egg-info" -o -name "*" -type d | grep -v "^\.$")
        echo "$injection_string" >> "$PKGDIR/PKG-INFO"
        (cd "$TMP" && tar -czf "$ARTIFACT_PATH" .)
    fi
    echo "($injection_string): patched $ARTIFACT_PATH"
    rm -rf "$TMP"
  done
fi
