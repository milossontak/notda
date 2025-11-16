# Jak vystavit službu na internet

## Možnost 1: Ngrok (nejrychlejší pro testování)

Ngrok vytvoří tunel z internetu na váš lokální server. Je to ideální pro testování a vývoj.

### Instalace ngrok

**Na macOS:**
```bash
# Pomocí Homebrew (doporučeno)
brew install ngrok/ngrok/ngrok

# Nebo stáhněte z https://ngrok.com/download
# a rozbalte do /usr/local/bin nebo do PATH
```

**Bez Homebrew:**
1. Jděte na https://ngrok.com/download
2. Stáhněte macOS verzi
3. Rozbalte a přesuňte `ngrok` do `/usr/local/bin`:
```bash
sudo mv ngrok /usr/local/bin/
sudo chmod +x /usr/local/bin/ngrok
```

### Použití ngrok

**Krok 1:** Spusťte vaši službu v jednom terminálu:
```bash
python3 app.py
```

**Krok 2:** V novém terminálu spusťte ngrok:
```bash
ngrok http 8000
```

**Krok 3:** Ngrok zobrazí něco jako:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Tuto URL můžete použít z internetu!**

### Automatické spuštění (doporučeno)

Místo ručního spouštění můžete použít náš skript:
```bash
python3 expose.py
```

Tento skript automaticky spustí službu i ngrok.

---

## Možnost 2: Cloudflare Tunnel (zdarma, bez registrace)

Cloudflare Tunnel je bezplatná alternativa k ngrok.

### Instalace

```bash
# Stáhněte z https://github.com/cloudflare/cloudflared/releases
# Nebo pomocí Homebrew:
brew install cloudflared
```

### Použití

```bash
# V jednom terminálu spusťte službu
python3 app.py

# V druhém terminálu spusťte tunnel
cloudflared tunnel --url http://localhost:8000
```

---

## Možnost 3: Cloudové nasazení (produkční řešení)

### Railway.app (doporučeno - velmi jednoduché)

1. Jděte na https://railway.app
2. Přihlaste se pomocí GitHubu
3. Klikněte na "New Project" → "Deploy from GitHub repo"
4. Připojte váš GitHub repozitář
5. Railway automaticky detekuje Python a spustí službu
6. Získáte veřejnou URL automaticky

**Potřebujete vytvořit `Procfile`:**
```
web: python3 app.py
```

### Render.com (zdarma tier)

1. Jděte na https://render.com
2. Přihlaste se pomocí GitHubu
3. Klikněte na "New" → "Web Service"
4. Připojte váš GitHub repozitář
5. Nastavte:
   - Build Command: `pip3 install -r requirements.txt`
   - Start Command: `python3 app.py`
6. Render poskytne veřejnou URL

### Fly.io

1. Nainstalujte flyctl: `brew install flyctl`
2. Přihlaste se: `fly auth login`
3. Vytvořte aplikaci: `fly launch`
4. Deploy: `fly deploy`

---

## Možnost 4: Vlastní server s veřejnou IP

Pokud máte server s veřejnou IP adresou:

1. Spusťte službu na serveru:
```bash
python3 app.py
```

2. Otevřete port 8000 v firewallu

3. Přístup přes: `http://VAŠE_IP:8000`

**⚠️ Pozor:** Pro produkci vždy používejte HTTPS (např. pomocí nginx reverse proxy s Let's Encrypt certifikátem)

---

## Testování veřejného přístupu

Po vystavení služby můžete otestovat:

```bash
# Nahraďte YOUR_URL vaší veřejnou URL
curl -X GET "YOUR_URL/version" \
  -H "x-api-key: your-api-key-here" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

---

## Doporučení

- **Pro rychlé testování:** Použijte ngrok nebo cloudflared
- **Pro produkci:** Použijte Railway, Render nebo Fly.io
- **Pro vlastní server:** Použijte nginx s HTTPS (Let's Encrypt)

---

## Bezpečnostní poznámky

⚠️ **Důležité:**
- Vždy změňte API klíč před vystavením na internet!
- Pro produkci používejte HTTPS
- Zvažte rate limiting pro ochranu před zneužitím
- Uložte API klíče do environment variables, ne do kódu

