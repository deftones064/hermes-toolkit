#!/usr/bin/env bash
set -euo pipefail

install -d /usr/local/lib/hermes-toolkit
cp -r toolkit /usr/local/lib/hermes-toolkit/

install -m 0755 hermes-settings /usr/local/bin/hermes-settings
ln -sf /usr/local/bin/hermes-settings /usr/local/bin/hermes-toolkit

if command -v systemctl >/dev/null 2>&1; then
  install -m 0644 hermes-toolkit-web.service /etc/systemd/system/hermes-toolkit-web.service
  systemctl daemon-reload
  systemctl enable hermes-toolkit-web.service
  systemctl restart hermes-toolkit-web.service
  echo "Web dashboard service enabled and restarted."
fi

echo "Installed Hermes Toolkit."
echo "CLI: hermes-toolkit status"
echo "Web: http://<host-ip>:8088"
