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

# 3. Instalace Pythonu a závislostí
dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel git

# 4. Vytvoření uživatele pro aplikaci
useradd -m -s /bin/bash eventapi

# 5. Přepnutí na uživatele
su - eventapi

# 6. Klonování repozitáře z GitHubu
cd ~
git clone https://github.com/milossontak/notda.git event-api
cd event-api

# 7. Vytvoření virtualního prostředí
python3 -m venv venv
source venv/bin/activate

# 8. Instalace závislostí
pip install --upgrade pip
pip install -r requirements.txt

# 9. Test spuštění (volitelné)
python app.py
# Měli byste vidět: "Spouštím server na 0.0.0.0:8000"
# Zastavte pomocí Ctrl+C

# 10. Vraťte se jako root
exit

# 11. Nastavení automatického spuštění po bootu
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

### Krok 3: Instalace Pythonu a potřebných nástrojů

```bash
# Instalace Pythonu 3 (obvykle Python 3.12 na CentOS Stream 10)
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel git

# Ověření instalace
python3 --version
# Mělo by zobrazit Python 3.8 nebo vyšší
```

### Krok 4: Vytvoření uživatele pro aplikaci

```bash
sudo useradd -m -s /bin/bash eventapi
```

### Krok 5: Klonování projektu z GitHubu

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

### Krok 6: Nastavení Python prostředí

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

### Krok 7: Test spuštění aplikace

```bash
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

### Krok 8: Nastavení automatického spuštění po bootu

**Vraťte se jako root:**
```bash
exit
```

**Vytvořte systemd service soubor:**
```bash
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

### Krok 9: Konfigurace firewallu

```bash
# Otevření portu 8000
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Ověření
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
# Z serveru
curl http://localhost:8000/health

# Z externího počítače
curl http://SERVER_IP:8000/health
```

### Webové rozhraní

Otevřete v prohlížeči:
- `http://SERVER_IP:8000` - Webové rozhraní
- `http://SERVER_IP:8000/health` - Health check

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
sudo ss -tlnp | grep 8000

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
# Najděte proces
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

**🎉 Hotovo!** Vaše aplikace je nyní nasazena na CentOS Stream 10 a automaticky se spustí při každém bootu!
