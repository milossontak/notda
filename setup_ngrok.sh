#!/bin/bash
# Skript pro nastavení ngrok authtoken

echo "=========================================="
echo "Nastavení ngrok authtoken"
echo "=========================================="
echo ""
echo "1. Vytvořte si účet na: https://dashboard.ngrok.com/signup"
echo "2. Přihlaste se a získejte authtoken na: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
read -p "Vložte váš ngrok authtoken: " authtoken

if [ -z "$authtoken" ]; then
    echo "❌ Authtoken nemůže být prázdný!"
    exit 1
fi

echo ""
echo "Nastavuji authtoken..."
ngrok config add-authtoken "$authtoken"

if [ $? -eq 0 ]; then
    echo "✓ Authtoken byl úspěšně nastaven!"
    echo ""
    echo "Nyní můžete spustit: python3 expose.py"
else
    echo "❌ Chyba při nastavování authtoken"
    exit 1
fi

