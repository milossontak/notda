# Restart služby na portu 80

Postup pro restart služby, aby běžela na portu 80 místo 8000.

---

## 🔄 Rychlý restart (pokud už máte správný service soubor)

```bash
# Restart služby
sudo systemctl restart event-api

# Kontrola stavu
sudo systemctl status event-api

# Ověření, že běží na portu 80
sudo ss -tlnp | grep :80
```

---

## ⚙️ Kompletní postup (aktualizace konfigurace)

### Krok 1: Zastavení služby

```bash
sudo systemctl stop event-api
```

### Krok 2: Aktualizace systemd service souboru

```bash
sudo nano /etc/systemd/system/event-api.service
```

**Ujistěte se, že obsahuje:**

```ini
[Unit]
Description=Event API FastAPI Application
After=network.target

[Service]
Type=simple
User=eventapi
Group=eventapi
WorkingDirectory=/home/eventapi/event-api
Environment="PATH=/home/eventapi/event-api/venv/bin"
Environment="PORT=80"
Environment="HOST=0.0.0.0"
Environment="API_KEY=your-secret-api-key-here"
AmbientCapabilities=CAP_NET_BIND_SERVICE
ExecStart=/home/eventapi/event-api/venv/bin/python /home/eventapi/event-api/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**⚠️ Důležité:**
- `Environment="PORT=80"` - port 80
- `AmbientCapabilities=CAP_NET_BIND_SERVICE` - oprávnění pro bind na port 80

### Krok 3: Načtení nové konfigurace

```bash
sudo systemctl daemon-reload
```

### Krok 4: Kontrola, zda port 80 není obsazený

```bash
# Zkontrolujte, co běží na portu 80
sudo lsof -i :80
# nebo
sudo ss -tlnp | grep :80

# Pokud běží Apache nebo Nginx, můžete je zastavit (pokud je nepotřebujete)
sudo systemctl stop httpd   # Apache
sudo systemctl stop nginx    # Nginx
```

### Krok 5: Spuštění služby

```bash
sudo systemctl start event-api
```

### Krok 6: Kontrola stavu

```bash
# Stav služby
sudo systemctl status event-api

# Logy
sudo journalctl -u event-api -n 50

# Ověření portu
sudo ss -tlnp | grep :80
```

### Krok 7: Testování

```bash
# Test z serveru
curl http://localhost/health

# Test z externího počítače
curl http://SERVER_IP/health
```

---

## 🔥 Firewall (pokud ještě není nastaven)

```bash
# Otevření portu 80
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload

# Ověření
sudo firewall-cmd --list-services
sudo firewall-cmd --list-ports
```

---

## ✅ Ověření, že vše funguje

```bash
# 1. Kontrola stavu služby
sudo systemctl status event-api

# 2. Kontrola portu
sudo ss -tlnp | grep :80
# Mělo by zobrazit: python proces naslouchající na :80

# 3. Test HTTP
curl http://localhost/health
# Mělo by vrátit: {"status":"ok",...}

# 4. Webové rozhraní
# Otevřete v prohlížeči: http://SERVER_IP
```

---

## 🆘 Troubleshooting

### Chyba: "Permission denied" nebo "Address already in use"

**Řešení 1: Zkontrolujte capabilities**

```bash
# Zkontrolujte, zda service soubor obsahuje AmbientCapabilities
grep AmbientCapabilities /etc/systemd/system/event-api.service
```

**Řešení 2: Zkontrolujte, zda port 80 není obsazený**

```bash
sudo lsof -i :80
# Ukončete proces, který port 80 používá
```

**Řešení 3: Alternativa - použijte setcap**

```bash
# Nastavení capability přímo na Python binárce
sudo setcap 'cap_net_bind_service=+ep' /home/eventapi/event-api/venv/bin/python3

# Pak můžete odstranit AmbientCapabilities z service souboru
```

### Služba se nespustí

```bash
# Zkontrolujte logy
sudo journalctl -u event-api -n 100

# Zkontrolujte syntaxi service souboru
sudo systemd-analyze verify /etc/systemd/system/event-api.service
```

---

## 📝 Shrnutí příkazů (pro rychlý restart)

```bash
# Pokud už máte správný service soubor:
sudo systemctl daemon-reload
sudo systemctl restart event-api
sudo systemctl status event-api
sudo ss -tlnp | grep :80
curl http://localhost/health
```

---

**Hotovo!** Služba by nyní měla běžet na portu 80. 🎉
