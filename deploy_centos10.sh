#!/bin/bash

# Automatický instalační skript pro CentOS Stream 10
# Tento skript nasadí aplikaci z GitHubu na CentOS Stream 10

set -e

echo "🚀 Automatické nasazení Event API na CentOS Stream 10"
echo "======================================================"
echo ""

# Kontrola, zda je skript spuštěn jako root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Tento skript musí být spuštěn jako root (použijte sudo)"
    exit 1
fi

# GitHub repozitář
GITHUB_REPO="https://github.com/milossontak/notda.git"
APP_USER="eventapi"
APP_DIR="/home/$APP_USER/event-api"
SERVICE_FILE="/etc/systemd/system/event-api.service"

# Krok 1: Aktualizace systému
echo "📦 Krok 1: Aktualizace systému..."
dnf update -y

# Krok 2: Instalace Pythonu a závislostí
echo ""
echo "🐍 Krok 2: Instalace Pythonu a závislostí..."
dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel git

# Ověření Pythonu
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION nainstalován"

# Krok 3: Vytvoření uživatele
echo ""
echo "👤 Krok 3: Vytvoření uživatele pro aplikaci..."
if id "$APP_USER" &>/dev/null; then
    echo "✓ Uživatel '$APP_USER' již existuje"
else
    useradd -m -s /bin/bash "$APP_USER"
    echo "✓ Uživatel '$APP_USER' vytvořen"
fi

# Krok 4: Klonování repozitáře
echo ""
echo "📥 Krok 4: Klonování repozitáře z GitHubu..."
if [ -d "$APP_DIR" ]; then
    echo "⚠️  Adresář $APP_DIR již existuje"
    read -p "Chcete ho přepsat? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$APP_DIR"
    else
        echo "❌ Instalace zrušena"
        exit 1
    fi
fi

# Klonování jako uživatel eventapi
sudo -u "$APP_USER" bash << EOF
cd ~
git clone $GITHUB_REPO event-api
cd event-api
echo "✓ Repozitář naklonován"
EOF

# Krok 5: Nastavení Python prostředí
echo ""
echo "🔧 Krok 5: Nastavení Python prostředí..."
sudo -u "$APP_USER" bash << EOF
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✓ Závislosti nainstalovány"
EOF

# Krok 6: Nastavení API klíče
echo ""
read -p "Zadejte API klíč (nebo stiskněte Enter pro výchozí): " API_KEY
API_KEY=${API_KEY:-your-secret-api-key-here}

# Krok 7: Vytvoření systemd service
echo ""
echo "⚙️  Krok 7: Vytvoření systemd service..."
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Event API FastAPI Application
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="PORT=8000"
Environment="HOST=0.0.0.0"
Environment="API_KEY=$API_KEY"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service soubor vytvořen"

# Krok 8: Nastavení oprávnění
echo ""
echo "🔐 Krok 8: Nastavení oprávnění..."
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod +x "$APP_DIR/app.py"

# Krok 9: Načtení a spuštění služby
echo ""
echo "🚀 Krok 9: Spuštění služby..."
systemctl daemon-reload
systemctl enable event-api
systemctl start event-api

# Krok 10: Firewall
echo ""
echo "🔥 Krok 10: Konfigurace firewallu..."
if systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-port=8000/tcp
    firewall-cmd --reload
    echo "✓ Port 8000 otevřen ve firewallu"
else
    echo "⚠️  Firewalld není aktivní, otevřete port 8000 ručně"
fi

# Krok 11: Kontrola stavu
echo ""
echo "✅ Instalace dokončena!"
echo ""
echo "📊 Stav služby:"
systemctl status event-api --no-pager -l || true

echo ""
echo "📋 Užitečné příkazy:"
echo "  - Zobrazení stavu: sudo systemctl status event-api"
echo "  - Zobrazení logů: sudo journalctl -u event-api -f"
echo "  - Restart služby: sudo systemctl restart event-api"
echo "  - Webové rozhraní: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
