#!/usr/bin/env bash
set -euo pipefail

install -m 0755 hermes-settings /usr/local/bin/hermes-settings

echo "Installed hermes-settings to /usr/local/bin/hermes-settings"
echo "Run: hermes-settings show"
