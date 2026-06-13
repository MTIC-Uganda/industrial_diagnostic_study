#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# Install PocketBase on the Hetzner server (run this via SSH as root)
#
#   ssh root@89.167.121.193
#   bash <(curl -s https://raw.githubusercontent.com/MTIC-Uganda/industrial_diagnostic_study/main/setup/hetzner_pocketbase.sh)
#
# Or copy the file and run: bash setup/hetzner_pocketbase.sh
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

PB_VERSION="0.22.7"
PB_DIR="/var/lib/pocketbase"
PB_BIN="/usr/local/bin/pocketbase"

echo "=== Installing PocketBase $PB_VERSION ==="

# Dependencies
apt-get update -q && apt-get install -y -q unzip curl

# Download binary
TMP=$(mktemp -d)
curl -fsSL "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip" \
     -o "$TMP/pb.zip"
unzip -q "$TMP/pb.zip" -d "$TMP"
mv "$TMP/pocketbase" "$PB_BIN"
chmod +x "$PB_BIN"
rm -rf "$TMP"
echo "Binary installed: $($PB_BIN --version)"

# Data directory
useradd --system --no-create-home --shell /usr/sbin/nologin pocketbase 2>/dev/null || true
mkdir -p "$PB_DIR"
chown pocketbase:pocketbase "$PB_DIR"

# systemd service
cat > /etc/systemd/system/pocketbase.service << 'EOF'
[Unit]
Description=PocketBase — MTIC Industrial Diagnostic Study
After=network.target

[Service]
Type=simple
User=pocketbase
WorkingDirectory=/var/lib/pocketbase
ExecStart=/usr/local/bin/pocketbase serve --http=0.0.0.0:8090
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pocketbase
systemctl restart pocketbase
sleep 2
systemctl is-active --quiet pocketbase && echo "PocketBase is running." || echo "ERROR: PocketBase failed to start."

echo ""
echo "============================================"
echo "  PocketBase is live at:"
echo "  Admin UI:  http://89.167.121.193:8090/_/"
echo ""
echo "  NEXT: open the admin UI in your browser,"
echo "  create the first admin account, then run:"
echo "    python db/pb_setup.py"
echo "============================================"
