# Nastavení HTTPS pro aplikaci na CentOS

Návod pro nastavení HTTPS pomocí Nginx reverse proxy a Let's Encrypt certifikátu.

---

## 📋 Předpoklady

- Aplikace běží na portu 80 (HTTP)
- Máte doménu ukázanou na IP adresu serveru
- SSH přístup k serveru s root/sudo oprávněními

---

## 🚀 Rychlý start

```bash
# 1. Instalace Nginx
sudo dnf install -y nginx

# 2. Instalace Certbot
sudo dnf install -y certbot python3-certbot-nginx

# 3. Konfigurace Nginx
sudo nano /etc/nginx/conf.d/event-api.conf
# (viz níže)

# 4. Test konfigurace
sudo nginx -t

# 5. Spuštění Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# 6. Získání SSL certifikátu
sudo certbot --nginx -d your-domain.com

# Hotovo! Aplikace bude dostupná na https://your-domain.com
```

---

## 🔧 Podrobný postup

### Krok 1: Instalace Nginx

```bash
sudo dnf install -y nginx
```

### Krok 2: Konfigurace Nginx jako reverse proxy

Vytvořte konfigurační soubor:

```bash
sudo nano /etc/nginx/conf.d/event-api.conf
```

**Přidejte následující obsah (nahraďte `your-domain.com` vaší doménou):**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS (bude aktivní po získání certifikátu)
    # return 301 https://$server_name$request_uri;

    # Dočasně: proxy na aplikaci (před získáním certifikátu)
    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (pokud budete potřebovat)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**⚠️ Poznámka:** Aplikace běží na portu 80, takže Nginx musí běžet na jiném portu nebo použít jinou IP. Upravíme to tak, aby aplikace běžela na portu 8000 a Nginx na portu 80.

### Krok 3: Změna portu aplikace na 8000

Aplikace musí běžet na jiném portu než Nginx. Změňme ji na port 8000:

```bash
# Upravte service soubor
sudo nano /etc/systemd/system/event-api.service
```

**Změňte:**
```ini
Environment="PORT=80"
```

**Na:**
```ini
Environment="PORT=8000"
```

**A odstraňte (už není potřeba pro port 8000):**
```ini
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

**Celý service soubor by měl vypadat:**
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
Environment="PORT=8000"
Environment="HOST=0.0.0.0"
Environment="API_KEY=your-secret-api-key-here"
ExecStart=/home/eventapi/event-api/venv/bin/python /home/eventapi/event-api/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Reload a restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart event-api
sudo systemctl status event-api
```

### Krok 4: Aktualizace Nginx konfigurace

```bash
sudo nano /etc/nginx/conf.d/event-api.conf
```

**Aktualizovaná konfigurace:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Proxy na aplikaci běžící na portu 8000
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Krok 5: Test Nginx konfigurace

```bash
sudo nginx -t
```

Mělo by zobrazit: `syntax is ok` a `test is successful`

### Krok 6: Spuštění Nginx

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

### Krok 7: Firewall

```bash
# Otevření portů pro HTTP a HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Ověření
sudo firewall-cmd --list-services
```

### Krok 8: Instalace Certbot

```bash
sudo dnf install -y certbot python3-certbot-nginx
```

### Krok 9: Získání SSL certifikátu

```bash
# Získání certifikátu (nahraďte your-domain.com)
sudo certbot --nginx -d your-domain.com

# Nebo pro více domén
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Certbot automaticky:
- Získá certifikát z Let's Encrypt
- Upraví Nginx konfiguraci pro HTTPS
- Nastaví automatické obnovování

### Krok 10: Ověření automatického obnovování

```bash
# Test obnovování certifikátu
sudo certbot renew --dry-run
```

---

## ✅ Ověření HTTPS

```bash
# Test HTTPS endpointu
curl https://your-domain.com/health

# Test v prohlížeči
# Otevřete: https://your-domain.com
```

---

## 🔄 Aktualizace Nginx konfigurace po Certbot

Po spuštění `certbot --nginx` bude Nginx konfigurace automaticky upravena. Měla by vypadat přibližně takto:

```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = your-domain.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name your-domain.com;
    return 404; # managed by Certbot
}
```

---

## 🛠️ Užitečné příkazy

```bash
# Restart Nginx
sudo systemctl restart nginx

# Zobrazení Nginx logů
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Kontrola certifikátu
sudo certbot certificates

# Ruční obnovení certifikátu
sudo certbot renew

# Zobrazení stavu služeb
sudo systemctl status nginx
sudo systemctl status event-api
```

---

## 🔒 Bezpečnostní doporučení

1. **Firewall**: Omezte přístup pouze na porty 80 a 443
2. **SSL/TLS**: Certifikát se automaticky obnovuje každých 90 dní
3. **Nginx**: Pravidelně aktualizujte Nginx pro bezpečnostní záplaty
4. **Rate limiting**: Zvažte přidání rate limitingu v Nginx

---

## 🆘 Troubleshooting

### Certbot nemůže získat certifikát

**Problém:** Certbot potřebuje ověřit doménu přes HTTP na portu 80.

**Řešení:**
```bash
# Ujistěte se, že port 80 je otevřený
sudo firewall-cmd --list-services

# Zkontrolujte, že Nginx běží
sudo systemctl status nginx

# Zkontrolujte DNS záznamy
dig your-domain.com
```

### Nginx neproxy požadavky správně

**Řešení:**
```bash
# Zkontrolujte Nginx logy
sudo tail -f /var/log/nginx/error.log

# Zkontrolujte, že aplikace běží na portu 8000
sudo ss -tlnp | grep :8000

# Test proxy
curl http://localhost:8000/health
```

### Certifikát vypršel

**Řešení:**
```bash
# Ruční obnovení
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx
```

---

## 📝 Shrnutí změn

1. ✅ Aplikace běží na portu 8000 (místo 80)
2. ✅ Nginx běží na portu 80 a proxy na aplikaci
3. ✅ Certbot získal SSL certifikát
4. ✅ HTTPS je aktivní na portu 443
5. ✅ HTTP automaticky přesměrovává na HTTPS

---

**🎉 Hotovo!** Vaše aplikace je nyní dostupná přes HTTPS na `https://your-domain.com`!
