# Testy

Tato složka obsahuje testovací skripty pro aplikaci.

## 📁 Soubory

### `test_api.py`
Python skript pro testování API endpointů.

**Použití:**
```bash
# Základní test
python3 tests/test_api.py

# Nebo s aktivovaným venv
source venv/bin/activate
python tests/test_api.py
```

**Konfigurace:**
Před spuštěním upravte v souboru:
- `API_KEY` - váš API klíč
- `BASE_URL` - URL aplikace (výchozí: http://localhost:8000)

### `test_version.sh`
Shell skript pro rychlý test version endpointu.

**Použití:**
```bash
./tests/test_version.sh

# Nebo s vlastní URL
./tests/test_version.sh "https://your-domain.com"
```

## 🧪 Co testují

- **test_api.py**: Kompletní testování všech API endpointů
- **test_version.sh**: Rychlý test version endpointu

## 📝 Poznámky

- Ujistěte se, že aplikace běží před spuštěním testů
- Pro produkční testy změňte BASE_URL na produkční URL
