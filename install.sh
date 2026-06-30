#!/usr/bin/env bash
set -euo pipefail

install -d /usr/local/lib/hermes-toolkit
cp -r toolkit /usr/local/lib/hermes-toolkit/

install -m 0755 hermes-settings /usr/local/bin/hermes-settings

echo "Installed Hermes Toolkit."
echo "Run: hermes-settings status"
