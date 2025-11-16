# Řešení problému s Ngrok Free Tier Warning Page

## Problém

Ngrok free tier zobrazuje warning page, která může blokovat automatické volání API. Dostáváte chybu:
```json
{
    "errors": [
        {
            "code": "EVENT_API_UNREACHABLE",
            "message": "EventAPI at URL 'https://...ngrok-free.dev' unreachable."
        }
    ]
}
```

## Řešení

### Možnost 1: Přidat hlavičku do volání (nejrychlejší)

Při volání API přidejte hlavičku:
```
ngrok-skip-browser-warning: true
```

**Příklad s curl:**
```bash
curl -X GET "https://javier-multisaccate-calculably.ngrok-free.dev/version" \
  -H "x-api-key: 123456" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f" \
  -H "ngrok-skip-browser-warning: true"
```

**Příklad s Python requests:**
```python
import requests

headers = {
    "x-api-key": "123456",
    "x-correlation-id": "71f415f4-412d-4c55-af05-15d1e0389f8f",
    "ngrok-skip-browser-warning": "true"  # Přidat tuto hlavičku
}

response = requests.get(
    "https://javier-multisaccate-calculably.ngrok-free.dev/version",
    headers=headers
)
```

### Možnost 2: Použít ngrok s vlastní doménou (placený)

Pokud máte ngrok placený účet, můžete použít vlastní doménu bez warning page:
```bash
ngrok http 8000 --domain=your-domain.ngrok.io
```

### Možnost 3: Použít Cloudflare Tunnel (doporučeno)

Cloudflare Tunnel nemá warning page a je zdarma:

```bash
# 1. Nainstalujte cloudflared
brew install cloudflared

# 2. Spusťte službu
python3 app.py

# 3. V novém terminálu spusťte tunnel
cloudflared tunnel --url http://localhost:8000
```

Cloudflare Tunnel vám poskytne URL bez warning page.

### Možnost 4: Použít cloudové řešení (produkce)

Pro produkci doporučuji použít:
- **Railway.app** - https://railway.app
- **Render.com** - https://render.com
- **Fly.io** - https://fly.io

Tyto služby poskytují stabilní URL bez warning page.

## Testování

Otestujte, zda API funguje s hlavičkou:

```bash
curl -X GET "https://javier-multisaccate-calculably.ngrok-free.dev/version" \
  -H "x-api-key: 123456" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f" \
  -H "ngrok-skip-browser-warning: true"
```

Měli byste dostat:
```json
{"version":"2.0"}
```

## Informace pro volající systém

Pokud voláte API z jiného systému (např. bankovní systém), musíte zajistit, aby přidával hlavičku `ngrok-skip-browser-warning: true` do všech HTTP požadavků.

**Alternativně:** Použijte Cloudflare Tunnel nebo cloudové řešení, které nemá tento problém.

