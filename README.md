# Event API Service

Služba pro přijímání eventů podle OpenAPI specifikace [schemas/Event-API-v20-SNAPSHOT.yaml](schemas/Event-API-v20-SNAPSHOT.yaml).

## Instalace

1. Vytvořte virtualní prostředí (doporučeno):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate     # Windows
```

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

**Nebo bez venv:**
```bash
pip3 install -r requirements.txt
```

## Spuštění

### Lokální spuštění

**S virtualním prostředím (doporučeno):**
```bash
# Aktivace venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate     # Windows

# Spuštění
python app.py
```

**Bez venv:**
```bash
python3 app.py
```

Služba poběží na `http://localhost:8000`

### Vystavení na internet

Pro vystavení služby na internet můžete použít několik možností:

#### 1. Ngrok (nejjednodušší pro testování)

**⚠️ Poznámka:** Ngrok vyžaduje účet a authtoken (zdarma).

1. Nainstalujte ngrok: `brew install ngrok/ngrok/ngrok` nebo z https://ngrok.com/download
2. Vytvořte si účet na: https://dashboard.ngrok.com/signup
3. Získejte authtoken na: https://dashboard.ngrok.com/get-started/your-authtoken
4. Nastavte authtoken:
```bash
ngrok config add-authtoken VÁŠ_AUTHTOKEN
```
Nebo použijte pomocný skript:
```bash
./setup_ngrok.sh
```

5. Spusťte službu pomocí:
```bash
python3 expose.py
```

Nebo ručně ve dvou terminálech:
```bash
# Terminál 1:
python3 app.py

# Terminál 2:
ngrok http 8000
```

Ngrok vám poskytne veřejnou URL (např. `https://abc123.ngrok.io`)

#### 2. Cloudflare Tunnel (zdarma, bez registrace)

Alternativa k ngrok, která nevyžaduje registraci:

1. Nainstalujte: `brew install cloudflared`
2. Spusťte službu: `python3 app.py`
3. V novém terminálu: `cloudflared tunnel --url http://localhost:8000`

Nebo použijte pomocný skript:
```bash
./expose_cloudflare.sh
```

#### 3. Cloudové řešení

Pro produkční nasazení doporučuji:
- **Heroku**: `heroku create` a `git push heroku main`
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Fly.io**: https://fly.io

#### 4. VPS server (CentOS/Linux)

Pro nasazení na vlastní VPS server s automatickým spuštěním po bootu:
- **CentOS Stream 10 z GitHubu**: Viz [docs/CENTOS_STREAM_10_DEPLOY.md](docs/CENTOS_STREAM_10_DEPLOY.md) ⭐ **Doporučeno pro rychlé nasazení**
- **Nastavení HTTPS**: Viz [docs/SETUP_HTTPS.md](docs/SETUP_HTTPS.md) - HTTPS s Nginx a Let's Encrypt
- **Troubleshooting**: Viz [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - řešení problémů

## Použití

### Webové rozhraní

Po spuštění služby otevřete v prohlížeči:
- Lokálně: `http://localhost:8000`
- Přes ngrok: použijte URL poskytnutou ngrokem

Webové rozhraní zobrazuje všechny přijaté eventy v reálném čase.

### API Endpointy

#### GET /version
Vrací verzi API (2.0)

**Hlavičky:**
- `x-api-key`: API klíč pro autentizaci
- `x-correlation-id`: GUID correlation ID

#### POST /subscriptions/{subscriptionId}/events
Přijímá eventy

**Hlavičky:**
- `x-api-key`: API klíč pro autentizaci
- `x-correlation-id`: GUID correlation ID
- `Accept-Language`: CZ nebo EN (volitelné, výchozí: CZ)

**Path parametr:**
- `subscriptionId`: GUID subscription ID

**Body:** JSON podle EventPayload schématu

### Konfigurace API klíče

Viz [docs/SETUP_API_KEY.md](docs/SETUP_API_KEY.md) pro podrobné instrukce.

Nebo v souboru `app.py` změňte:
```python
VALID_API_KEYS = {"123456"}  # Změňte na skutečný API klíč
```

Můžete přidat více klíčů:
```python
VALID_API_KEYS = {"key1", "key2", "key3"}
```

## Testování

### Použití testovacího skriptu

Nejjednodušší způsob testování:

```bash
python3 tests/test_api.py
```

Nezapomeňte předtím změnit `API_KEY` v souboru `tests/test_api.py` na stejný klíč jako v `app.py`.

### Manuální testování pomocí curl

```bash
# Test version endpointu
curl -X GET "http://localhost:8000/version" \
  -H "x-api-key: your-api-key-here" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"

# Test receive event endpointu
curl -X POST "http://localhost:8000/subscriptions/71f415f4-412d-4c55-af05-15d1e0389f8f/events" \
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

## Poznámky

- Eventy jsou ukládány v paměti (maximálně 1000). Pro produkci doporučuji použít databázi.
- API klíč by měl být v produkci uložen v environment variables.
- Pro produkční nasazení doporučuji použít HTTPS.

## 📁 Struktura projektu

```
notda/
├── app.py                      # Hlavní aplikace
├── expose.py                   # Skript pro vystavení na internet
├── requirements.txt            # Python závislosti
├── README.md                   # Tento soubor
│
├── docs/                       # 📚 Dokumentace
│   ├── README.md              # Index dokumentace
│   ├── CENTOS_STREAM_10_DEPLOY.md
│   ├── SETUP_HTTPS.md
│   └── ...
│
├── scripts/                    # 🔧 Skripty
│   ├── deployment/            # Nasazovací skripty
│   ├── development/           # Vývojářské skripty
│   └── tunneling/             # Tunnel skripty
│
├── config/                     # ⚙️ Konfigurační soubory
│   └── event-api.service      # Systemd service
│
├── tests/                      # 🧪 Testy
│   ├── test_api.py
│   └── test_version.sh
│
└── schemas/                    # 📋 API schémata
    └── Event-API-v20-SNAPSHOT.yaml
```

## 📚 Dokumentace

Všechna dokumentace je umístěna ve složce [`docs/`](docs/):

- **Nasazení**: [docs/CENTOS_STREAM_10_DEPLOY.md](docs/CENTOS_STREAM_10_DEPLOY.md) - Nasazení na CentOS Stream 10
- **HTTPS**: [docs/SETUP_HTTPS.md](docs/SETUP_HTTPS.md) - Nastavení HTTPS
- **API**: [docs/API_USAGE.md](docs/API_USAGE.md) - Použití API
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Řešení problémů
- **Kompletní seznam**: [docs/README.md](docs/README.md) - Přehled všech dokumentů

