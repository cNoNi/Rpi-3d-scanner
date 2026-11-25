#!/usr/bin/env bash
# Installs the scanner as a systemd service that starts on boot.
#
# Usage (on the Raspberry Pi, from anywhere):
#   bash scripts/install-service.sh            install / update and start
#   bash scripts/install-service.sh uninstall  stop and remove the service
#
# Optional WebSocket token for the phone: put it in /etc/default/rpi-3d-scanner
#   SCANNER_WS_TOKEN=your-secret
# then: sudo systemctl restart rpi-3d-scanner

set -euo pipefail

SERVICE=rpi-3d-scanner
UNIT_FILE=/etc/systemd/system/$SERVICE.service
ENV_FILE=/etc/default/$SERVICE
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="${SUDO_USER:-$(id -un)}"

if [[ "${1:-}" == "uninstall" ]]; then
    sudo systemctl disable --now "$SERVICE" 2>/dev/null || true
    sudo rm -f "$UNIT_FILE"
    sudo systemctl daemon-reload
    echo "Service removed ($ENV_FILE left in place)."
    exit 0
fi

if [[ "$RUN_USER" == "root" ]]; then
    echo "Run this as your normal user (it calls sudo itself), not as root." >&2
    exit 1
fi

echo "==> Installing system packages"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-lgpio

echo "==> Preparing virtualenv in $APP_DIR/.venv"
if [[ ! -x "$APP_DIR/.venv/bin/python" ]]; then
    python3 -m venv --system-site-packages "$APP_DIR/.venv"
fi
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "==> Creating $ENV_FILE (edit it to set SCANNER_WS_TOKEN)"
    echo "SCANNER_WS_TOKEN=" | sudo tee "$ENV_FILE" >/dev/null
    sudo chmod 600 "$ENV_FILE"
fi

echo "==> Writing $UNIT_FILE"
sudo tee "$UNIT_FILE" >/dev/null <<EOF
[Unit]
Description=Raspberry Pi 3D scanner
Wants=network-online.target
After=network-online.target

[Service]
User=$RUN_USER
SupplementaryGroups=gpio
WorkingDirectory=$APP_DIR
EnvironmentFile=-$ENV_FILE
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_DIR/.venv/bin/python app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE"
sudo systemctl restart "$SERVICE"

IP="$(hostname -I | awk '{print $1}')"
echo
echo "Done. Scanner runs at http://${IP:-<pi-ip>}:5000 and will start on every boot."
echo "Logs:    journalctl -u $SERVICE -f"
echo "Status:  systemctl status $SERVICE"
