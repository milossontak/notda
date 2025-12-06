# Návod pro nasazení na CentOS

Tento dokument popisuje kompletní postup nasazení FastAPI aplikace na CentOS server.

## 📋 Požadavky

- CentOS 7+ nebo CentOS Stream 8/9
- Root nebo sudo přístup
- Minimálně 1GB RAM
- Připojení k internetu

---

## 🚀 Krok 1: Aktualizace systému

```bash
sudo yum update -y
```

---

## 🐍 Krok 2: Instalace Pythonu 3.11

### CentOS 7

CentOS 7 má ve výchozím repozitáři pouze Python 3.6, takže potřebujeme nainstalovat Python 3.11 z EPEL nebo Software Collections.

**Možnost A: Python 3.11 z EPEL (doporučeno)**

```bash
# Instalace EPEL repozitáře
sudo yum install -y epel-release

# Instalace Pythonu 3.11 a potřebných nástrojů
sudo yum install -y python311 python311-pip python311-devel gcc

# Vytvoření symlinku (volitelné, pro snadnější použití)
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
```

**Možnost B: Kompilace z zdrojového kódu**

```bash
# Instalace build dependencies
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel

# Stažení a kompilace Pythonu 3.11
cd /tmp
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
tar xzf Python-3.11.0.tgz
cd Python-3.11.0
./configure --enable-optimizations
make altinstall

# Vytvoření symlinku
sudo ln -s /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -s /usr/local/bin/pip3.11 /usr/bin/pip3.11
```

### CentOS Stream 8/9 nebo Rocky Linux 8/9

```bash
# Instalace Pythonu 3.9 nebo 3.10 (dostupné ve výchozích repozitářích)
sudo dnf install -y python39 python39-pip python39-devel gcc
# nebo
sudo dnf install -y python310 python310-pip python310-devel gcc

# Nebo použijte python3 (obvykle Python 3.9+)
sudo dnf install -y python3 python3-pip python3-devel gcc
```

**Poznámka:** Python 3.11 nemusí být dostupný ve výchozích repozitářích. Python 3.9+ je dostačující pro tuto aplikaci.

**Ověření instalace:**

```bash
python3 --version
# Mělo by zobrazit: Python 3.8.x nebo vyšší

pip3 --version
# Mělo by zobrazit: pip x.x.x
```

**⚠️ Pokud Python 3.11 není dostupný:** Použijte Python 3.9 nebo vyšší. Aplikace funguje s Pythonem 3.8+. Viz [CENTOS_PYTHON_FIX.md](CENTOS_PYTHON_FIX.md) pro řešení problémů s instalací Pythonu.

---

## 📦 Krok 3: Příprava projektu

### 3.1 Vytvoření uživatele pro aplikaci (doporučeno)

```bash
# Vytvoření uživatele
sudo useradd -m -s /bin/bash eventapi

# Přepnutí na uživatele
sudo su - eventapi
```

### 3.2 Stažení nebo nahrání projektu

**Možnost A: Git clone (pokud máte projekt na GitHubu/GitLabu)**

```bash
cd ~
git clone https://github.com/VÁŠ_USERNAME/VÁŠ_REPO.git event-api
cd event-api
```

**Možnost B: Nahrání přes SCP (z vašeho lokálního počítače)**

```bash
# Z vašeho lokálního počítače:
scp -r /cesta/k/projektu eventapi@SERVER_IP:/home/eventapi/event-api
```

**Možnost C: Vytvoření projektu ručně**

```bash
mkdir -p ~/event-api
cd ~/event-api
# Nahrajte soubory app.py, requirements.txt, runtime.txt atd.
```

---

## 🔧 Krok 4: Nastavení Python prostředí

### 4.1 Vytvoření virtualního prostředí

```bash
cd ~/event-api

# Vytvoření venv (použijte python3 nebo python3.9/python3.10/python3.12 podle toho, co máte)
python3 -m venv venv
# nebo
python3.9 -m venv venv
# nebo
python3.10 -m venv venv

# Aktivace venv
source venv/bin/activate

# Ověření, že používáme správný Python
which python
python --version
# Mělo by zobrazit Python 3.8 nebo vyšší
```

### 4.2 Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

### 4.3 Instalace závislostí

```bash
# Instalace systémových závislostí pro Pillow (QR kód generování)
sudo yum install -y libjpeg-devel zlib-devel

# Instalace Python závislostí
pip install -r requirements.txt
```

**Ověření instalace:**

```bash
pip list
# Měli byste vidět: fastapi, uvicorn, pydantic, qrcode, Pillow, atd.
```

---

## ⚙️ Krok 5: Konfigurace aplikace

### 5.1 Nastavení environment variables

Vytvořte soubor `.env` (volitelné, nebo použijte systemd environment):

```bash
cd ~/event-api
nano .env
```

Přidejte:

```bash
PORT=8000
HOST=0.0.0.0
API_KEY=your-secret-api-key-here
```

**⚠️ Důležité:** Nikdy necommitujte `.env` do Gitu!

### 5.2 Test spuštění aplikace

```bash
# Ujistěte se, že jste v aktivovaném venv
source venv/bin/activate

# Spuštění aplikace
python app.py
```

Měli byste vidět:
```
Spouštím server na 0.0.0.0:8000
Webové rozhraní: http://localhost:8000
```

Otevřete v prohlížeči: `http://SERVER_IP:8000`

Pokud to funguje, zastavte aplikaci (Ctrl+C).

---

## 🔥 Krok 6: Konfigurace firewallu

### CentOS 7 (firewalld)

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Ověření
sudo firewall-cmd --list-ports
```

### CentOS 8/9 nebo pokud používáte iptables

```bash
# Firewalld (doporučeno)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Nebo iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo service iptables save  # CentOS 7
sudo iptables-save > /etc/sysconfig/iptables  # CentOS 8+
```

---

## 🎯 Krok 7: Nastavení automatického spuštění po bootu

### Možnost A: Automatické nastavení pomocí skriptu (doporučeno)

Nejjednodušší způsob je použít připravený skript:

```bash
# Zkopírujte skript na server a spusťte jako root
sudo bash setup_centos_autostart.sh
```

Skript vás provede nastavením a automaticky vytvoří systemd service.

### Možnost B: Ruční nastavení

**1. Vytvoření systemd service souboru:**

```bash
sudo nano /etc/systemd/system/event-api.service
```

**2. Přidejte následující obsah (upravte cesty podle vašeho nastavení):**

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

**⚠️ Důležité:** 
- Upravte cesty (`/home/eventapi/event-api`) podle vašeho nastavení
- Změňte `API_KEY` na váš skutečný API klíč
- Ujistěte se, že uživatel `eventapi` existuje

**Nastavení oprávnění:**

```bash
# Nastavení vlastníka souborů aplikace
sudo chown -R eventapi:eventapi /home/eventapi/event-api

# Nastavení oprávnění
sudo chmod +x /home/eventapi/event-api/app.py
```

**3. Načtení a spuštění služby:**

```bash
# Načtení nového service souboru
sudo systemctl daemon-reload

# Povolení automatického spuštění při bootu (důležité!)
sudo systemctl enable event-api

# Spuštění služby
sudo systemctl start event-api

# Kontrola stavu
sudo systemctl status event-api

# Zobrazení logů
sudo journalctl -u event-api -f
```

**✅ Po těchto krocích se aplikace automaticky spustí při každém bootu serveru!**

**Užitečné příkazy:**

```bash
# Zastavení služby
sudo systemctl stop event-api

# Restart služby
sudo systemctl restart event-api

# Zobrazení logů
sudo journalctl -u event-api -n 50

# Sledování logů v reálném čase
sudo journalctl -u event-api -f
```

---

## 🌐 Krok 8: Nginx reverse proxy (volitelné, doporučeno pro produkci)

Pro produkční nasazení doporučuji použít Nginx jako reverse proxy před FastAPI aplikací.

### 8.1 Instalace Nginx

```bash
sudo yum install -y nginx
```

### 8.2 Konfigurace Nginx

```bash
sudo nano /etc/nginx/conf.d/event-api.conf
```

Přidejte:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Nebo IP adresa

    location / {
        proxy_pass http://127.0.0.1:8000;
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

**Test konfigurace:**

```bash
sudo nginx -t
```

**Spuštění Nginx:**

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

**Firewall pro HTTP/HTTPS:**

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 8.3 SSL certifikát (Let's Encrypt)

```bash
# Instalace certbot
sudo yum install -y certbot python3-certbot-nginx

# Získání certifikátu
sudo certbot --nginx -d your-domain.com

# Automatické obnovování
sudo certbot renew --dry-run
```

---

## ✅ Krok 9: Ověření nasazení

### 9.1 Kontrola, že aplikace běží

```bash
# Kontrola procesu
ps aux | grep python

# Kontrola portu
sudo netstat -tlnp | grep 8000
# nebo
sudo ss -tlnp | grep 8000

# Test HTTP požadavku
curl http://localhost:8000/health
```

### 9.2 Testování API

```bash
# Health check
curl http://SERVER_IP:8000/health

# Version endpoint (vyžaduje x-correlation-id header)
curl -X GET "http://SERVER_IP:8000/version" \
  -H "x-correlation-id: 71f415f4-412d-4c55-af05-15d1e0389f8f"
```

### 9.3 Webové rozhraní

Otevřete v prohlížeči:
- `http://SERVER_IP:8000` (přímý přístup)
- `http://your-domain.com` (přes Nginx)

---

## 🔍 Troubleshooting

### Aplikace se nespustí

```bash
# Zkontrolujte logy
sudo journalctl -u event-api -n 100

# Zkontrolujte, zda je port volný
sudo lsof -i :8000

# Zkontrolujte oprávnění
ls -la /home/eventapi/event-api/
```

### Port je obsazený

```bash
# Najděte proces používající port
sudo lsof -i :8000

# Ukončete proces
sudo kill -9 PID
```

### Python moduly nejsou nalezeny

```bash
# Ujistěte se, že používáte správné venv
source /home/eventapi/event-api/venv/bin/activate
which python
pip list

# Reinstalujte závislosti
pip install -r requirements.txt
```

### Firewall blokuje připojení

```bash
# Zkontrolujte firewall pravidla
sudo firewall-cmd --list-all

# Otevřete port
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### SELinux problémy (CentOS)

```bash
# Zkontrolujte SELinux status
getenforce

# Pokud je Enforcing, můžete dočasně povolit přístup
sudo setsebool -P httpd_can_network_connect 1

# Nebo nastavte SELinux na Permissive (pro testování)
sudo setenforce 0
```

---

## 📝 Rychlý start (shrnující příkazy)

```bash
# 1. Aktualizace systému
sudo yum update -y

# 2. Instalace Pythonu 3.11
sudo yum install -y epel-release
sudo yum install -y python311 python311-pip python311-devel gcc libjpeg-devel zlib-devel

# 3. Vytvoření uživatele
sudo useradd -m -s /bin/bash eventapi
sudo su - eventapi

# 4. Příprava projektu
cd ~
git clone YOUR_REPO_URL event-api
# nebo nahrajte soubory ručně
cd event-api

# 5. Vytvoření venv a instalace závislostí
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. Test spuštění (volitelné, pro ověření)
python app.py
# Ctrl+C pro zastavení

# 7. Nastavení automatického spuštění po bootu (jako root)
exit

# Možnost A: Použít automatický skript
sudo bash /cesta/k/projektu/setup_centos_autostart.sh

# Možnost B: Ruční nastavení
sudo cp /cesta/k/projektu/event-api.service /etc/systemd/system/
# Upravte cesty v souboru podle vašeho nastavení
sudo nano /etc/systemd/system/event-api.service
sudo systemctl daemon-reload
sudo systemctl enable event-api
sudo systemctl start event-api

# 8. Kontrola stavu
sudo systemctl status event-api

# 9. Firewall
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# ✅ Hotovo! Aplikace se nyní spustí automaticky při každém bootu
```

---

## 🔒 Bezpečnostní doporučení

1. **API klíč**: Použijte silný API klíč a uložte ho v environment variables
2. **Firewall**: Omezte přístup pouze na potřebné porty
3. **SSL**: Pro produkci vždy používejte HTTPS (Let's Encrypt)
4. **Uživatel**: Spouštějte aplikaci pod neprivilegovaným uživatelem (ne root)
5. **Aktualizace**: Pravidelně aktualizujte systém a Python balíčky
6. **Logy**: Monitorujte logy pro podezřelou aktivitu

---

## 📚 Užitečné odkazy

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Systemd Service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Nginx Reverse Proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 💡 Tipy

- Pro produkci použijte více worker procesů: `uvicorn app:app --workers 4`
- Nastavte logování do souboru místo stdout
- Použijte process manager jako Supervisor nebo systemd (doporučeno)
- Pro vysokou dostupnost zvažte load balancer (Nginx, HAProxy)

---

**Hotovo!** Vaše aplikace by nyní měla běžet na CentOS serveru. 🎉
