#!/bin/bash
# Skript pro restart serveru

echo "Hledám běžící server..."
PID=$(lsof -ti :8000)

if [ ! -z "$PID" ]; then
    echo "Ukončuji server na portu 8000 (PID: $PID)..."
    kill $PID
    sleep 2
    echo "✓ Server ukončen"
else
    echo "Server neběží na portu 8000"
fi

echo ""
echo "Spouštím nový server..."
python3 app.py

