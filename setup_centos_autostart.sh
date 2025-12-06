#!/bin/bash

# Skript pro nastavení automatického spuštění aplikace po bootu na CentOS
# Tento skript nastaví systemd service pro automatické spuštění

set -e

echo "🔧 Nastavení automatického spuštění aplikace po bootu"
echo "======================================================"
echo ""

# Kontrola, zda je skript spuštěn jako root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Tento skript musí být spuštěn jako root (použijte sudo)"
    exit 1
fi

# Zjištění cesty k projektu
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_FILE="$SCRIPT_DIR/event-api.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Soubor event-api.service nebyl nalezen v $SCRIPT_DIR"
    exit 1
fi

# Zjištění uživatele a cesty k aplikaci
read -p "Zadejte uživatelské jméno pro aplikaci [eventapi]: " APP_USER
APP_USER=${APP_USER:-eventapi}

read -p "Zadejte cestu k aplikaci [/home/$APP_USER/event-api]: " APP_DIR
APP_DIR=${APP_DIR:-/home/$APP_USER/event-api}

# Kontrola existence adresáře
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Adresář $APP_DIR neexistuje!"
    exit 1
fi

# Kontrola existence venv
if [ ! -d "$APP_DIR/venv" ]; then
    echo "❌ Virtualní prostředí nebylo nalezeno v $APP_DIR/venv"
    echo "Vytvořte venv pomocí: python3.11 -m venv venv"
    exit 1
fi

# Kontrola existence app.py
if [ ! -f "$APP_DIR/app.py" ]; then
    echo "❌ Soubor app.py nebyl nalezen v $APP_DIR"
    exit 1
fi

# Nastavení API klíče
read -p "Zadejte API klíč (nebo stiskněte Enter pro výchozí): " API_KEY
API_KEY=${API_KEY:-your-secret-api-key-here}

# Vytvoření systemd service souboru
SERVICE_CONTENT="[Unit]
Description=Event API FastAPI Application
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=\"PATH=$APP_DIR/venv/bin\"
Environment=\"PORT=8000\"
Environment=\"HOST=0.0.0.0\"
Environment=\"API_KEY=$API_KEY\"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"

echo ""
echo "📝 Vytvářím systemd service soubor..."
echo "$SERVICE_CONTENT" > /etc/systemd/system/event-api.service

# Nastavení oprávnění
echo "🔐 Nastavuji oprávnění..."
chown -R $APP_USER:$APP_USER "$APP_DIR"
chmod +x "$APP_DIR/app.py"

# Načtení systemd
echo "🔄 Načítám systemd konfiguraci..."
systemctl daemon-reload

# Povolení automatického spuštění
echo "✅ Povoluji automatické spuštění při bootu..."
systemctl enable event-api

# Spuštění služby
echo "🚀 Spouštím službu..."
systemctl start event-api

# Kontrola stavu
echo ""
echo "📊 Stav služby:"
systemctl status event-api --no-pager

echo ""
echo "✅ Hotovo! Aplikace je nastavena pro automatické spuštění po bootu."
echo ""
echo "📋 Užitečné příkazy:"
echo "  - Zobrazení stavu: sudo systemctl status event-api"
echo "  - Zobrazení logů: sudo journalctl -u event-api -f"
echo "  - Restart služby: sudo systemctl restart event-api"
echo "  - Zastavení služby: sudo systemctl stop event-api"
echo "  - Zakázání autostartu: sudo systemctl disable event-api"
echo ""
