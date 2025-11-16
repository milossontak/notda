#!/bin/bash
# Skript pro kontrolu a uvolnění portu 8000

PORT=${1:-8000}

echo "Kontroluji port $PORT..."

if lsof -ti :$PORT > /dev/null 2>&1; then
    PID=$(lsof -ti :$PORT)
    echo "⚠️  Port $PORT je obsazený procesem PID $PID"
    echo "Ukončuji proces..."
    kill $PID
    sleep 1
    if lsof -ti :$PORT > /dev/null 2>&1; then
        echo "❌ Nepodařilo se ukončit proces. Zkuste ručně: kill -9 $PID"
        exit 1
    else
        echo "✓ Port $PORT je nyní volný"
    fi
else
    echo "✓ Port $PORT je volný"
fi

