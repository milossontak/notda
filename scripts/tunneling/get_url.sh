#!/bin/bash
# Skript pro získání veřejné URL z ngrok nebo cloudflared

echo "=========================================="
echo "Veřejná URL vašeho API"
echo "=========================================="
echo ""

# Zkusit ngrok
if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    echo "📍 Ngrok běží!"
    echo ""
    URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else 'Nenalezeno')" 2>/dev/null)
    if [ ! -z "$URL" ] && [ "$URL" != "Nenalezeno" ]; then
        echo "🌐 Veřejná URL: $URL"
        echo ""
        echo "API endpointy:"
        echo "  Version: $URL/version"
        echo "  Events:  $URL/subscriptions/{subscriptionId}/events"
        echo "  Web UI:  $URL/"
        echo ""
        echo "Ngrok dashboard: http://localhost:4040"
    else
        echo "❌ Nepodařilo se získat URL z ngrok"
    fi
# Zkusit cloudflared
elif pgrep -f cloudflared > /dev/null; then
    echo "📍 Cloudflare Tunnel běží!"
    echo ""
    echo "Cloudflare Tunnel zobrazuje URL při spuštění."
    echo "Zkontrolujte výstup z cloudflared procesu."
    echo ""
    echo "Nebo použijte: ps aux | grep cloudflared"
else
    echo "❌ Žádný tunnel neběží!"
    echo ""
    echo "Spusťte:"
    echo "  python3 expose.py          (pro ngrok)"
    echo "  ./expose_cloudflare.sh      (pro Cloudflare Tunnel)"
fi

echo "=========================================="

