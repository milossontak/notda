#!/bin/bash
# Skript pro testování /version endpointu

API_URL="${1:-https://javier-multisaccate-calculably.ngrok-free.dev}"
API_KEY="${2:-your-api-key-here}"

echo "Testování endpointu: $API_URL/version"
echo ""

# Generovat GUID
CORRELATION_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

echo "Correlation ID: $CORRELATION_ID"
echo "API Key: $API_KEY"
echo ""

curl -X GET "$API_URL/version" \
  -H "x-api-key: $API_KEY" \
  -H "x-correlation-id: $CORRELATION_ID" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -v 2>&1 | grep -E "(< HTTP|{|\"version\")"

