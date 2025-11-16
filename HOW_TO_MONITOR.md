# Jak sledovat příchozí volání API

## 1. V terminálu (logy serveru)

Když spustíte server pomocí `python3 app.py`, uvidíte v terminálu všechny příchozí požadavky:

```
2025-11-15 22:51:42 - __main__ - INFO - 📥 INCOMING: GET /version from 127.0.0.1
2025-11-15 22:51:42 - __main__ - INFO - 📤 RESPONSE: GET /version -> 200 (2.45ms)
2025-11-15 22:51:45 - __main__ - INFO - 📥 INCOMING: POST /subscriptions/.../events from 192.168.1.100
2025-11-15 22:51:45 - __main__ - INFO - 📤 RESPONSE: POST /subscriptions/.../events -> 204 (5.12ms)
```

## 2. Webové rozhraní (zobrazení eventů)

Otevřete v prohlížeči:
- Lokálně: `http://localhost:8000/`
- Veřejně: `https://your-url.trycloudflare.com/`

Zobrazí se všechny přijaté eventy s:
- Časem přijetí
- Subscription ID
- Correlation ID
- Jazykem
- Kompletním payloadem

## 3. API endpoint pro historii požadavků

Získejte historii všech příchozích požadavků:

```bash
curl http://localhost:8000/requests
```

Nebo veřejně:
```bash
curl https://your-url.trycloudflare.com/requests
```

Odpověď obsahuje:
- Celkový počet požadavků
- Seznam všech požadavků s detaily:
  - Čas
  - HTTP metoda
  - Cesta
  - IP adresa volajícího
  - User-Agent
  - Status code
  - Doba zpracování
  - Všechny hlavičky

## 4. API endpoint pro eventy

Získejte pouze přijaté eventy:

```bash
curl http://localhost:8000/events
```

## 5. Sledování v reálném čase

### Automatické obnovování na webu

Na webové stránce zaškrtněte "Automatické obnovování" - stránka se bude obnovovat každých 5 sekund.

### Tail logů serveru

Pokud spouštíte server v terminálu, můžete sledovat logy v reálném čase. Všechny příchozí požadavky se zobrazují okamžitě.

## 6. Příklady použití

### Zobrazit posledních 10 požadavků:

```bash
curl http://localhost:8000/requests | python3 -m json.tool | tail -50
```

### Najít všechny požadavky na /version:

```bash
curl http://localhost:8000/requests | python3 -c "import sys, json; data=json.load(sys.stdin); [print(r) for r in data['requests'] if r['path'] == '/version']"
```

### Zobrazit všechny chyby (status >= 400):

```bash
curl http://localhost:8000/requests | python3 -c "import sys, json; data=json.load(sys.stdin); [print(r) for r in data['requests'] if r.get('status_code', 200) >= 400]"
```

## 7. Vymazání historie

### Vymazat historii požadavků:

```bash
curl -X DELETE http://localhost:8000/requests
```

### Vymazat všechny eventy:

```bash
curl -X DELETE http://localhost:8000/events
```

## 8. Co se loguje

Pro každý požadavek se ukládá:
- ✅ Čas příchozího požadavku
- ✅ HTTP metoda (GET, POST, atd.)
- ✅ Cesta (path)
- ✅ Query parametry
- ✅ IP adresa volajícího
- ✅ User-Agent
- ✅ Všechny HTTP hlavičky
- ✅ Status code odpovědi
- ✅ Doba zpracování v milisekundách
- ✅ Chyby (pokud nastaly)

## 9. Omezení

- Historie požadavků: maximálně 500 záznamů (nejnovější)
- Historie eventů: maximálně 1000 záznamů (nejnovější)
- Data jsou uložena pouze v paměti - po restartu serveru se smažou

## 10. Pro produkci

Pro produkční nasazení doporučuji:
- Použít databázi místo paměti
- Přidat persistentní logování do souboru
- Použít nástroje jako Prometheus + Grafana pro monitoring
- Nastavit alerting pro chyby

