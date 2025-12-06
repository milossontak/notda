# 🚀 Rychlý start - CentOS s automatickým spuštěním po bootu

Tento návod vám pomůže rychle nastavit aplikaci na CentOS tak, aby se **automaticky spouštěla po každém bootu**.

---

## ⚡ Nejrychlejší způsob (5 kroků)

### 1️⃣ Příprava systému (jako root)

```bash
# Aktualizace systému
sudo yum update -y
# nebo pro CentOS Stream 8+: sudo dnf update -y

# Instalace Pythonu (zkuste podle vaší verze CentOS)
# Pro CentOS Stream 8/9:
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel

# Pro CentOS Stream 10:
sudo dnf install -y python3.12 python3.12-pip python3.12-devel gcc libjpeg-devel zlib-devel
# nebo jednoduše: sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel

# Pro CentOS 7:
sudo yum install -y epel-release
sudo yum install -y python39 python39-pip python39-devel gcc libjpeg-devel zlib-devel

# Ověření instalace
python3 --version
# Mělo by zobrazit Python 3.8 nebo vyšší

# Vytvoření uživatele pro aplikaci
sudo useradd -m -s /bin/bash eventapi
```

**⚠️ Pokud se zobrazí chyba "No match for argument: python311", použijte řešení z [CENTOS_PYTHON_FIX.md](CENTOS_PYTHON_FIX.md)**

### 2️⃣ Instalace aplikace (jako uživatel eventapi)

```bash
# Přepnutí na uživatele
sudo su - eventapi

# Stažení nebo nahrání projektu
cd ~
# Nahrajte soubory: app.py, requirements.txt, event-api.service, setup_centos_autostart.sh

# Vytvoření venv a instalace závislostí
# Použijte python3 (nebo python3.9, python3.10, python3.12 podle toho, co máte nainstalováno)
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Test (volitelné)

```bash
# Ověření, že aplikace funguje
python app.py
# Měli byste vidět: "Spouštím server na 0.0.0.0:8000"
# Zastavte pomocí Ctrl+C
```

### 4️⃣ Nastavení automatického spuštění po bootu

```bash
# Vraťte se zpět jako root
exit

# Spusťte automatický setup skript
sudo bash /home/eventapi/event-api/setup_centos_autostart.sh
```

Skript vás provede nastavením:
- Zadejte uživatelské jméno (nebo Enter pro výchozí `eventapi`)
- Zadejte cestu k aplikaci (nebo Enter pro výchozí `/home/eventapi/event-api`)
- Zadejte API klíč (nebo Enter pro výchozí)

### 5️⃣ Firewall a hotovo!

```bash
# Otevření portu 8000
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Kontrola, že služba běží
sudo systemctl status event-api
```

**✅ Hotovo!** Aplikace se nyní automaticky spustí při každém bootu serveru.

---

## 🔍 Ověření, že vše funguje

```bash
# Kontrola stavu služby
sudo systemctl status event-api

# Zobrazení logů
sudo journalctl -u event-api -f

# Test HTTP požadavku
curl http://localhost:8000/health

# Test z externího počítače
curl http://SERVER_IP:8000/health
```

---

## 📋 Užitečné příkazy pro správu

```bash
# Zobrazení stavu služby
sudo systemctl status event-api

# Zobrazení logů (posledních 50 řádků)
sudo journalctl -u event-api -n 50

# Sledování logů v reálném čase
sudo journalctl -u event-api -f

# Restart služby
sudo systemctl restart event-api

# Zastavení služby
sudo systemctl stop event-api

# Spuštění služby
sudo systemctl start event-api

# Zakázání automatického spuštění (pokud potřebujete)
sudo systemctl disable event-api

# Znovu povolení automatického spuštění
sudo systemctl enable event-api
```

---

## 🎯 Co se stane při bootu?

1. Systém se načte
2. Síť se inicializuje
3. Systemd automaticky spustí službu `event-api`
4. Aplikace poběží na portu 8000
5. Pokud aplikace spadne, systemd ji automaticky restartuje

---

## ⚠️ Troubleshooting

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

### Aplikace se nespouští po bootu

```bash
# Zkontrolujte, zda je služba povolena
sudo systemctl is-enabled event-api

# Pokud není, povolte ji
sudo systemctl enable event-api
```

---

## 📚 Podrobnější návod

Pro kompletní návod s vysvětlením všech kroků viz: [CENTOS_SETUP.md](CENTOS_SETUP.md)

---

**🎉 Gratulujeme! Vaše aplikace běží automaticky po každém bootu CentOS serveru!**
