#!/bin/bash
# Skript pro restart Cloudflare Tunnel

echo "=========================================="
echo "Restart Cloudflare Tunnel"
echo "=========================================="
echo ""

# Ukončit existující tunnel
if pgrep -f "cloudflared tunnel" > /dev/null; then
    echo "Ukončuji existující Cloudflare Tunnel..."
    pkill -f "cloudflared tunnel"
    sleep 2
fi

# Zkontrolovat, zda server běží
if ! lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Server neběží na portu 8000!"
    echo "Spusťte nejdřív: python3 app.py"
    exit 1
fi

echo "✓ Server běží na portu 8000"
echo ""
echo "Spouštím Cloudflare Tunnel..."
echo ""

# Spustit tunnel
cloudflared tunnel --url http://localhost:8000

