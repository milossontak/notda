# 🚀 Nasazení aplikace na CentOS Stream 10 z GitHubu

Kompletní návod pro nasazení aplikace na CentOS Stream 10 přímo z GitHub repozitáře.

---

## 📋 Předpoklady

- CentOS Stream 10 server s root nebo sudo přístupem
- SSH přístup k serveru
- GitHub repozitář: `https://github.com/milossontak/notda.git`

---

## ⚡ Rychlý start (kopírovat a vložit)

```bash
# 1. Připojte se k serveru přes SSH
ssh root@VAŠE_IP_ADRESA

# 2. Aktualizace systému
dnf update -y

# 3. Instalace Git (pokud není nainstalovaný)
dnf install -y git

# 4. Instalace Pythonu a závislostí
dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel

# 5. Vytvoření uživatele pro aplikaci
useradd -m -s /bin/bash eventapi

# 6. Přepnutí na uživatele
su - eventapi

# 7. Klonování repozitáře z GitHubu
cd ~
git clone https://github.com/milossontak/notda.git event-api
cd event-api

# 8. Vytvoření virtualního prostředí
python3 -m venv venv
source venv/bin/activate

# 9. Instalace závislostí
pip install --upgrade pip
pip install -r requirements.txt

# 10. Test spuštění (volitelné)
# POZOR: Pro test na portu 80 potřebujete root nebo capabilities
# Pro test použijte port 8000: PORT=8000 python app.py
python app.py
# Měli byste vidět: "Spouštím server na 0.0.0.0:80"
# Zastavte pomocí Ctrl+C

# 11. Vraťte se jako root
exit

# 12. Nastavení automatického spuštění po bootu
# Použijte připravený skript nebo vytvořte systemd service ručně
```

---

## 🔧 Podrobný postup

### Krok 1: Připojení k serveru

```bash
ssh root@VAŠE_IP_ADRESA
# nebo pokud máte jiného uživatele s sudo
ssh uživatel@VAŠE_IP_ADRESA
```

### Krok 2: Aktualizace systému

```bash
sudo dnf update -y
```

### Krok 3: Instalace Git a potřebných nástrojů

**⚠️ Pokud vidíte chybu "git: command not found", nejdřív nainstalujte Git:**

```bash
# Instalace Git
sudo dnf install -y git

# Ověření instalace
git --version
# Mělo by zobrazit: git version 2.x.x
```

### Krok 4: Instalace Pythonu a dalších závislostí

```bash
# Instalace Pythonu 3 (obvykle Python 3.12 na CentOS Stream 10)
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel

# Ověření instalace
python3 --version
# Mělo by zobrazit Python 3.8 nebo vyšší
```

### Krok 5: Vytvoření uživatele pro aplikaci

```bash
sudo useradd -m -s /bin/bash eventapi
```

### Krok 6: Klonování projektu z GitHubu

```bash
# Přepnutí na uživatele
sudo su - eventapi

# Klonování repozitáře
cd ~
git clone https://github.com/milossontak/notda.git event-api
cd event-api

# Ověření, že soubory jsou stažené
ls -la
# Měli byste vidět: app.py, requirements.txt, atd.
```

### Krok 7: Nastavení Python prostředí

```bash
# Vytvoření virtualního prostředí
python3 -m venv venv

# Aktivace venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Instalace závislostí
pip install -r requirements.txt

# Ověření instalace
pip list
# Měli byste vidět: fastapi, uvicorn, pydantic, qrcode, Pillow, atd.
```

### Krok 8: Test spuštění aplikace

```bash
# Spuštění aplikace
python app.py
```

**⚠️ Poznámka:** Pro testování na portu 80 potřebujete root oprávnění. Pro test použijte port 8000:

```bash
PORT=8000 python app.py
```

Měli byste vidět:
```
Spouštím server na 0.0.0.0:8000
Webové rozhraní: http://localhost:8000
```

Otevřete v prohlížeči: `http://SERVER_IP:8000`

**V produkci bude aplikace běžet na portu 80** (bez nutnosti zadávat port v URL).

Pokud to funguje, zastavte aplikaci (Ctrl+C).

### Krok 9: Nastavení automatického spuštění po bootu

**Vraťte se jako root:**
```bash
exit
```

**Vytvořte systemd service soubor:**
```bash
# Zkopírujte service soubor z projektu
sudo cp /home/eventapi/event-api/config/event-api.service /etc/systemd/system/event-api.service

# Nebo vytvořte ručně
sudo nano /etc/systemd/system/event-api.service
```

**Vložte následující obsah (upravte API_KEY):**
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
# Capability pro binding na port 80 (místo spuštění jako root)
AmbientCapabilities=CAP_NET_BIND_SERVICE
ExecStart=/home/eventapi/event-api/venv/bin/python /home/eventapi/event-api/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**⚠️ Poznámka:** Port 80 vyžaduje speciální oprávnění. Používáme `AmbientCapabilities=CAP_NET_BIND_SERVICE`, což umožní neprivilegovanému uživateli bindovat na port 80 bez nutnosti spouštět službu jako root.

**Nastavení oprávnění a spuštění služby:**
```bash
# Nastavení vlastníka
sudo chown -R eventapi:eventapi /home/eventapi/event-api

# Načtení systemd
sudo systemctl daemon-reload

# Povolení automatického spuštění při bootu
sudo systemctl enable event-api

# Spuštění služby
sudo systemctl start event-api

# Kontrola stavu
sudo systemctl status event-api
```

### Krok 10: Konfigurace firewallu

```bash
# Otevření portu 80 (HTTP)
sudo firewall-cmd --permanent --add-service=http
# nebo explicitně port 80
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload

# Ověření
sudo firewall-cmd --list-services
sudo firewall-cmd --list-ports
```

---

## ✅ Ověření nasazení

### Kontrola stavu služby

```bash
sudo systemctl status event-api
```

### Zobrazení logů

```bash
# Posledních 50 řádků
sudo journalctl -u event-api -n 50

# Sledování v reálném čase
sudo journalctl -u event-api -f
```

### Test HTTP požadavku

```bash
# Z serveru (port 80 - standardní HTTP port)
curl http://localhost/health
# nebo explicitně
curl http://localhost:80/health

# Z externího počítače
curl http://SERVER_IP/health
# nebo
curl http://SERVER_IP:80/health
```

### Restart služby na portu 80

Pokud potřebujete restartovat službu, aby běžela na portu 80:

```bash
# 1. Zastavení služby
sudo systemctl stop event-api

# 2. Aktualizace service souboru (ujistěte se, že PORT=80 a AmbientCapabilities je nastaveno)
sudo nano /etc/systemd/system/event-api.service

# 3. Načtení nové konfigurace
sudo systemctl daemon-reload

# 4. Spuštění služby
sudo systemctl start event-api

# 5. Kontrola
sudo systemctl status event-api
sudo ss -tlnp | grep :80
```

Viz také: [RESTART_TO_PORT_80.md](RESTART_TO_PORT_80.md) pro podrobný návod.

### Webové rozhraní

Otevřete v prohlížeči:
- `http://SERVER_IP` - Webové rozhraní (port 80 je výchozí)
- `http://SERVER_IP/health` - Health check

---

## 🔄 Aktualizace aplikace (po změnách na GitHubu)

Když uděláte změny v kódu a pushnete je na GitHub, můžete aktualizovat aplikaci na serveru:

```bash
# Přepnutí na uživatele aplikace
sudo su - eventapi

# Přejít do adresáře projektu
cd ~/event-api

# Stáhnout nejnovější změny z GitHubu
git pull origin main

# Aktivovat venv
source venv/bin/activate

# Aktualizovat závislosti (pokud se změnily)
pip install -r requirements.txt

# Vraťte se jako root
exit

# Restart služby
sudo systemctl restart event-api

# Kontrola stavu
sudo systemctl status event-api
```

---

## 🛠️ Užitečné příkazy

```bash
# Zobrazení stavu služby
sudo systemctl status event-api

# Restart služby
sudo systemctl restart event-api

# Zastavení služby
sudo systemctl stop event-api

# Spuštění služby
sudo systemctl start event-api

# Zobrazení logů
sudo journalctl -u event-api -f

# Kontrola, zda port naslouchá
sudo ss -tlnp | grep :80
# nebo
sudo ss -tlnp | grep http

# Kontrola procesu
ps aux | grep python
```

---

## 🔒 Bezpečnostní doporučení

1. **Změňte API klíč** v systemd service souboru (`/etc/systemd/system/event-api.service`)
2. **Firewall**: Omezte přístup pouze na potřebné porty
3. **SSL**: Pro produkci použijte HTTPS (Let's Encrypt + Nginx)
4. **Uživatel**: Aplikace běží pod neprivilegovaným uživatelem (eventapi)
5. **Aktualizace**: Pravidelně aktualizujte systém a Python balíčky

---

## 🆘 Troubleshooting

### Služba se nespustí

```bash
# Zkontrolujte logy
sudo journalctl -u event-api -n 100

# Zkontrolujte, zda existuje venv
ls -la /home/eventapi/event-api/venv

# Zkontrolujte oprávnění
ls -la /home/eventapi/event-api/
```

### Port je obsazený

```bash
# Najděte proces na portu 80
sudo lsof -i :80
# nebo
sudo ss -tlnp | grep :80

# Ukončete proces
sudo kill -9 PID

# Pokud je to webový server (např. Apache/Nginx), můžete ho zastavit
sudo systemctl stop httpd  # Apache
sudo systemctl stop nginx   # Nginx
```

### Python moduly nejsou nalezeny

```bash
# Ujistěte se, že používáte správné venv
source /home/eventapi/event-api/venv/bin/activate
which python
pip list
```

### Git pull nefunguje

```bash
# Zkontrolujte připojení k internetu
ping github.com

# Zkontrolujte Git konfiguraci
git remote -v
```

---

## 📝 Shrnutí příkazů (pro kopírování)

```bash
# Kompletní instalace na jednom řádku (jako root)
dnf update -y && dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel git && useradd -m -s /bin/bash eventapi && su - eventapi -c "cd ~ && git clone https://github.com/milossontak/notda.git event-api && cd event-api && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt" && echo "✅ Instalace dokončena! Nyní nastavte systemd service."
```

---

## 🔒 Nastavení HTTPS (volitelné)

Pro produkční nasazení doporučuji nastavit HTTPS pomocí Nginx a Let's Encrypt:

- **Kompletní návod**: Viz [SETUP_HTTPS.md](SETUP_HTTPS.md) - nastavení HTTPS s Nginx reverse proxy

**Rychlý přehled:**
1. Instalace Nginx: `sudo dnf install -y nginx`
2. Změna portu aplikace na 8000 (Nginx bude na 80)
3. Konfigurace Nginx jako reverse proxy
4. Instalace Certbot: `sudo dnf install -y certbot python3-certbot-nginx`
5. Získání certifikátu: `sudo certbot --nginx -d your-domain.com`

---

**🎉 Hotovo!** Vaše aplikace je nyní nasazena na CentOS Stream 10 a automaticky se spustí při každém bootu!
