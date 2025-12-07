#!/bin/bash
# Startovací skript pro Event API službu

echo "Spouštím Event API službu..."

# Zkontrolovat, zda existuje venv
if [ ! -d "venv" ]; then
    echo "⚠️  Virtualní prostředí neexistuje. Vytvářím venv..."
    python3 -m venv venv
    echo "📦 Instaluji závislosti..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

# Použít Python z venv
echo "🚀 Spouštím aplikaci z venv..."
./venv/bin/python app.py

