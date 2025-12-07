#!/bin/bash
# Skript pro přepnutí z ngrok na Cloudflare Tunnel

echo "=========================================="
echo "Přepnutí na Cloudflare Tunnel"
echo "=========================================="
echo ""

# Zkontrolovat, zda je cloudflared nainstalován
if ! command -v cloudflared &> /dev/null; then
    echo "❌ Cloudflared není nainstalován!"
    echo ""
    echo "Instalace:"
    echo "  brew install cloudflared"
    echo ""
    exit 1
fi

# Ukončit ngrok pokud běží
if pgrep -f "ngrok http" > /dev/null; then
    echo "Ukončuji ngrok..."
    pkill -f "ngrok http"
    sleep 1
fi

# Ukončit server pokud běží
if lsof -ti :8000 > /dev/null 2>&1; then
    echo "Ukončuji server na portu 8000..."
    lsof -ti :8000 | xargs kill
    sleep 1
fi

echo ""
echo "✓ Ngrok a server ukončeny"
echo ""
echo "Nyní spusťte:"
echo "  1. python3 app.py"
echo "  2. V novém terminálu: cloudflared tunnel --url http://localhost:8000"
echo ""
echo "Cloudflare Tunnel vám poskytne URL bez warning page!"

