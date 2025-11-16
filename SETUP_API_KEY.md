# Jak nastavit API klíč

API klíč můžete nastavit dvěma způsoby:

## Možnost 1: Přímo v kódu (pro testování)

Otevřete soubor `app.py` a na řádku **33** změňte:

```python
VALID_API_KEYS = {"your-api-key-here"}  # ⚠️ ZMĚŇTE NA SVŮJ API KLÍČ!
```

Na například:

```python
VALID_API_KEYS = {"muj-tajny-api-klic-123"}
```

**⚠️ Pozor:** Tento způsob není bezpečný pro produkci! API klíč bude viditelný v kódu.

---

## Možnost 2: Přes environment variable (doporučeno)

### Na macOS/Linux:

**Při spuštění:**
```bash
API_KEY="muj-tajny-api-klic-123" python3 app.py
```

**Nebo exportovat před spuštěním:**
```bash
export API_KEY="muj-tajny-api-klic-123"
python3 app.py
```

**Pro expose.py:**
```bash
export API_KEY="muj-tajny-api-klic-123"
python3 expose.py
```

### Trvalé nastavení (doporučeno):

Přidejte do `~/.zshrc` nebo `~/.bashrc`:
```bash
export API_KEY="muj-tajny-api-klic-123"
```

Pak načtěte:
```bash
source ~/.zshrc  # nebo source ~/.bashrc
```

---

## Možnost 3: Více API klíčů

Pokud potřebujete více API klíčů, můžete nastavit:

**V kódu:**
```python
VALID_API_KEYS = {"key1", "key2", "key3"}
```

**Přes environment variable (oddělené čárkou):**
```bash
export API_KEY="key1,key2,key3"
```

A upravit v `app.py`:
```python
API_KEY_ENV = os.getenv("API_KEY")
if API_KEY_ENV:
    VALID_API_KEYS = set(API_KEY_ENV.split(","))
```

---

## Ověření nastavení

Po nastavení API klíče můžete otestovat:

```bash
./test_version.sh
```

Nebo ručně:
```bash
curl -X GET "https://javier-multisaccate-calculably.ngrok-free.dev/version" \
  -H "x-api-key: muj-tajny-api-klic-123" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

---

## Bezpečnostní doporučení

1. **Nikdy necommitovat API klíče do Gitu**
   - Přidejte `app.py` do `.gitignore` pokud obsahuje skutečné klíče
   - Nebo používejte pouze environment variables

2. **Pro produkci vždy používejte environment variables**

3. **Používejte silné, náhodné API klíče**
   - Minimálně 32 znaků
   - Kombinace písmen, čísel a speciálních znaků

4. **Pravidelně rotujte API klíče**

---

## Aktuální nastavení

Chcete-li zjistit, jaký API klíč je aktuálně nastaven, podívejte se na výstup při spuštění serveru:

```
⚠️  Používám výchozí API klíč. Pro produkci nastavte API_KEY environment variable nebo změňte hodnotu zde.
```

Nebo:
```
✓ API klíč načten z environment variable
```

