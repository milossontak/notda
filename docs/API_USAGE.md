# Jak správně volat Event API

## Endpoint: GET /version

### Povinné hlavičky:
- `x-api-key`: API klíč pro autentizaci
- `x-correlation-id`: GUID correlation ID (formát: 8-4-4-4-12)

### Příklad volání pomocí curl:

```bash
curl -X GET "https://javier-multisaccate-calculably.ngrok-free.dev/version" \
  -H "x-api-key: your-api-key-here" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

### Příklad volání pomocí JavaScript (fetch):

```javascript
fetch('https://javier-multisaccate-calculably.ngrok-free.dev/version', {
  method: 'GET',
  headers: {
    'x-api-key': 'your-api-key-here',
    'x-correlation-id': '71f415f4-412d-4c55-af05-15d1e0389f8f'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Příklad volání pomocí Python (requests):

```python
import requests
import uuid

url = "https://javier-multisaccate-calculably.ngrok-free.dev/version"
headers = {
    "x-api-key": "your-api-key-here",
    "x-correlation-id": str(uuid.uuid4())
}

response = requests.get(url, headers=headers)
print(response.json())
```

### Očekávaná odpověď:

```json
{
  "version": "2.0"
}
```

---

## Endpoint: POST /subscriptions/{subscriptionId}/events

### Povinné hlavičky:
- `x-api-key`: API klíč pro autentizaci
- `x-correlation-id`: GUID correlation ID (formát: 8-4-4-4-12)
- `Accept-Language`: CZ nebo EN (volitelné, výchozí: CZ)

### Příklad volání pomocí curl:

```bash
curl -X POST "https://javier-multisaccate-calculably.ngrok-free.dev/subscriptions/71f415f4-412d-4c55-af05-15d1e0389f8f/events" \
  -H "x-api-key: your-api-key-here" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f" \
  -H "Accept-Language: CZ" \
  -H "Content-Type: application/json" \
  -d '{
    "eventCount": 1,
    "bookTransactions": [{
      "transactionType": "DOMESTIC",
      "bookingDate": "2024-01-15",
      "lastUpdated": "2024-01-15T10:30:00Z",
      "iban": "CZ6508000000192000145399",
      "amount": {"value": 1000.50, "currency": "CZK"},
      "creditDebitIndicator": "CREDIT"
    }]
  }'
```

### Očekávaná odpověď:

Status code: `204 No Content` (bez těla odpovědi)

---

## Generování GUID (Correlation ID)

### V bash:
```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

### V Python:
```python
import uuid
correlation_id = str(uuid.uuid4())
```

### Online:
- https://www.uuidgenerator.net/
- https://www.uuid.org/

---

## Testovací skripty

### Test /version endpointu:
```bash
./tests/test_version.sh
```

### Test s vlastními parametry:
```bash
./tests/test_version.sh "https://javier-multisaccate-calculably.ngrok-free.dev" "your-api-key"
```

---

## Důležité poznámky

1. **API klíč**: Musí být stejný jako v `app.py` (řádek 19)
   ```python
   VALID_API_KEYS = {"your-api-key-here"}
   ```

2. **Correlation ID**: Musí být ve formátu GUID (8-4-4-4-12)
   - ✅ Správně: `71f415f4-412d-4c55-af05-15d1e0389f8f`
   - ❌ Špatně: `123` nebo `test-id`

3. **Subscription ID**: Také musí být ve formátu GUID

4. **Chyby**: Pokud chybí hlavičky, dostanete 400 s popisem chyby

