# Řešení problémů s dostupností API

## Problém: "EVENT_API_UNREACHABLE"

Pokud dostáváte chybu, že API není dostupné, zkuste následující:

### 1. Ověřte, že server běží

```bash
# Zkontrolujte, zda server běží na portu 8000
lsof -i :8000

# Otestujte lokální připojení
curl http://localhost:8000/health
```

### 2. Ověřte, že Cloudflare Tunnel běží

```bash
# Zkontrolujte proces cloudflared
ps aux | grep cloudflared

# Otestujte health check endpoint (bez autentizace)
curl https://collections-palm-reputation-inf.trycloudflare.com/health
```

### 3. Otestujte všechny endpointy

**Health check (bez autentizace):**
```bash
curl https://collections-palm-reputation-inf.trycloudflare.com/health
```

**Version endpoint:**
```bash
curl -X GET "https://collections-palm-reputation-inf.trycloudflare.com/version" \
  -H "x-api-key: 123456" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

**HEAD request (pro health checks):**
```bash
curl -I "https://collections-palm-reputation-inf.trycloudflare.com/version" \
  -H "x-api-key: 123456" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

### 4. Možné příčiny problému

#### A) Timeout
Volající systém může mít příliš krátký timeout. Zkuste zvýšit timeout na alespoň 10 sekund.

#### B) SSL/TLS problémy
Některé systémy mohou mít problém s SSL certifikáty Cloudflare. Zkuste:
- Ověřit, že systém důvěřuje Cloudflare certifikátům
- Použít HTTP/2 (Cloudflare to podporuje)

#### C) Firewall nebo síťové omezení
Zkontrolujte, zda volající systém může přistupovat k `*.trycloudflare.com` doménám.

#### D) User-Agent nebo jiné hlavičky
Některé systémy mohou vyžadovat specifické hlavičky. Zkuste přidat:
```bash
-H "User-Agent: EventAPI-Client/1.0"
-H "Accept: application/json"
```

### 5. Alternativní řešení

#### Použít ngrok s hlavičkou
```bash
# Spusťte ngrok
ngrok http 8000

# Použijte URL s hlavičkou ngrok-skip-browser-warning
curl -X GET "https://your-ngrok-url.ngrok-free.dev/version" \
  -H "x-api-key: 123456" \
  -H "x-correlation-id: ..." \
  -H "ngrok-skip-browser-warning: true"
```

#### Použít cloudové řešení
Pro produkci použijte:
- **Railway.app** - https://railway.app
- **Render.com** - https://render.com
- **Fly.io** - https://fly.io

Tyto služby poskytují stabilní URL bez problémů s tunnel službami.

### 6. Debugging

Zapněte verbose logging v curl:
```bash
curl -v "https://collections-palm-reputation-inf.trycloudflare.com/version" \
  -H "x-api-key: 123456" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

Zkontrolujte logy serveru:
```bash
tail -f /tmp/app_server.log
```

### 7. Kontaktní informace

Pokud problém přetrvává:
1. Zkontrolujte logy Cloudflare Tunnel
2. Ověřte, že všechny procesy běží
3. Zkuste restartovat server a tunnel
4. Zvažte použití cloudového řešení pro produkci

