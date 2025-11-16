#!/bin/bash
# Alternativní skript pro vystavení služby pomocí Cloudflare Tunnel
# Cloudflare Tunnel je zdarma a nevyžaduje registraci

echo "=========================================="
echo "Vystavení služby pomocí Cloudflare Tunnel"
echo "=========================================="
echo ""

# Zkontrolovat, zda je cloudflared nainstalován
if ! command -v cloudflared &> /dev/null; then
    echo "❌ Cloudflared není nainstalován!"
    echo ""
    echo "Instalace:"
    echo "  brew install cloudflared"
    echo ""
    echo "Nebo stáhněte z: https://github.com/cloudflare/cloudflared/releases"
    exit 1
fi

PORT=${1:-8000}

echo "Spouštím službu na portu $PORT..."
echo "V novém terminálu spusťte: python3 app.py"
echo ""
echo "Stiskněte Enter, když bude služba běžet..."
read

echo ""
echo "Spouštím Cloudflare Tunnel..."
cloudflared tunnel --url http://localhost:$PORT

