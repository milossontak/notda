#!/bin/bash

# Instalační skript pro CentOS
# Tento skript automaticky nastaví prostředí pro FastAPI aplikaci na CentOS

set -e  # Zastavit při chybě

echo "🚀 Instalace Event API na CentOS"
echo "=================================="
echo ""

# Kontrola, zda je skript spuštěn jako root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Tento skript musí být spuštěn jako root (použijte sudo)"
    exit 1
fi

# Detekce verze CentOS
if [ -f /etc/redhat-release ]; then
    CENTOS_VERSION=$(cat /etc/redhat-release)
    echo "📋 Detekovaný systém: $CENTOS_VERSION"
else
    echo "⚠️  Varování: Není detekován CentOS/RHEL systém"
fi

# Krok 1: Aktualizace systému
echo ""
echo "📦 Krok 1: Aktualizace systému..."
yum update -y

# Krok 2: Instalace Pythonu 3.11
echo ""
echo "🐍 Krok 2: Instalace Pythonu 3.11..."

# Kontrola, zda už není nainstalován Python 3.11
if command -v python3.11 &> /dev/null; then
    echo "✓ Python 3.11 je již nainstalován"
    python3.11 --version
else
    echo "Instaluji Python 3.11..."
    
    # Instalace EPEL
    if ! rpm -qa | grep -q epel-release; then
        echo "Instaluji EPEL repozitář..."
        yum install -y epel-release
    fi
    
    # Instalace Pythonu 3.11
    yum install -y python311 python311-pip python311-devel gcc
    
    echo "✓ Python 3.11 nainstalován"
    python3.11 --version
fi

# Krok 3: Instalace systémových závislostí
echo ""
echo "📚 Krok 3: Instalace systémových závislostí..."
yum install -y libjpeg-devel zlib-devel

# Krok 4: Vytvoření uživatele pro aplikaci
echo ""
echo "👤 Krok 4: Vytvoření uživatele pro aplikaci..."
if id "eventapi" &>/dev/null; then
    echo "✓ Uživatel 'eventapi' již existuje"
else
    useradd -m -s /bin/bash eventapi
    echo "✓ Uživatel 'eventapi' vytvořen"
fi

# Krok 5: Nastavení projektu
echo ""
echo "📁 Krok 5: Příprava projektu..."
APP_DIR="/home/eventapi/event-api"

if [ -d "$APP_DIR" ]; then
    echo "⚠️  Adresář $APP_DIR již existuje"
    read -p "Chcete pokračovat? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    mkdir -p "$APP_DIR"
fi

# Nastavení vlastníka
chown -R eventapi:eventapi "$APP_DIR"

echo ""
echo "✅ Základní instalace dokončena!"
echo ""
echo "📝 Další kroky:"
echo "1. Přepněte se na uživatele eventapi: sudo su - eventapi"
echo "2. Přejděte do adresáře projektu: cd ~/event-api"
echo "3. Nahrajte soubory aplikace (app.py, requirements.txt, atd.)"
echo "4. Vytvořte virtualní prostředí: python3.11 -m venv venv"
echo "5. Aktivujte venv: source venv/bin/activate"
echo "6. Nainstalujte závislosti: pip install -r requirements.txt"
echo "7. Otestujte aplikaci: python app.py"
echo ""
echo "📖 Pro kompletní návod viz: CENTOS_SETUP.md"
echo ""
