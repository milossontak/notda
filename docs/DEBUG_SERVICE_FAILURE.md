# Debugování selhání služby event-api

Pokud služba neběží a zobrazuje `status=1/FAILURE`, použijte tento postup.

---

## 🔍 Krok 1: Zobrazení detailních logů

```bash
# Zobrazení posledních 100 řádků logů
sudo journalctl -u event-api -n 100

# Zobrazení logů od posledního spuštění
sudo journalctl -u event-api --since "5 minutes ago"

# Sledování logů v reálném čase (zatímco restartujete službu)
sudo journalctl -u event-api -f
```

**Toto vám ukáže konkrétní chybovou zprávu!**

---

## 🛠️ Časté problémy a řešení

### Problém 1: Permission denied na portu 80

**Chyba v logu:**
```
PermissionError: [Errno 13] Permission denied
```

**Řešení:**

```bash
# Zkontrolujte, zda service soubor obsahuje AmbientCapabilities
grep AmbientCapabilities /etc/systemd/system/event-api.service

# Pokud chybí, přidejte do [Service] sekce:
sudo nano /etc/systemd/system/event-api.service
# Přidejte řádek: AmbientCapabilities=CAP_NET_BIND_SERVICE

# Alternativa: Nastavte capability přímo na Python binárce
sudo setcap 'cap_net_bind_service=+ep' /home/eventapi/event-api/venv/bin/python3

# Pak reload a restart
sudo systemctl daemon-reload
sudo systemctl restart event-api
```

### Problém 2: Port 80 je již obsazený

**Chyba v logu:**
```
OSError: [Errno 98] Address already in use
```

**Řešení:**

```bash
# Najděte proces používající port 80
sudo lsof -i :80
# nebo
sudo ss -tlnp | grep :80

# Ukončete proces (např. Apache nebo Nginx)
sudo systemctl stop httpd   # Apache
sudo systemctl stop nginx    # Nginx

# Nebo zabijte konkrétní proces
sudo kill -9 PID

# Pak restart služby
sudo systemctl restart event-api
```

### Problém 3: Chybějící Python moduly

**Chyba v logu:**
```
ModuleNotFoundError: No module named 'fastapi'
# nebo jiný modul
```

**Řešení:**

```bash
# Přepněte se na uživatele aplikace
sudo su - eventapi

# Aktivujte venv
cd ~/event-api
source venv/bin/activate

# Reinstalujte závislosti
pip install --upgrade pip
pip install -r requirements.txt

# Ověření
pip list | grep fastapi

# Vraťte se zpět
exit

# Restart služby
sudo systemctl restart event-api
```

### Problém 4: Chybějící soubory nebo špatná cesta

**Chyba v logu:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Řešení:**

```bash
# Zkontrolujte, zda adresář existuje
ls -la /home/eventapi/event-api/

# Zkontrolujte, zda app.py existuje
ls -la /home/eventapi/event-api/app.py

# Zkontrolujte, zda venv existuje
ls -la /home/eventapi/event-api/venv/bin/python

# Pokud chybí, přeinstalujte aplikaci podle návodu
```

### Problém 5: Chyba v Python kódu

**Chyba v logu:**
```
SyntaxError: ...
# nebo jiná Python chyba
```

**Řešení:**

```bash
# Otestujte aplikaci ručně
sudo su - eventapi
cd ~/event-api
source venv/bin/activate
python app.py

# Pokud to funguje ručně, problém je v systemd konfiguraci
# Zkontrolujte service soubor
exit
sudo cat /etc/systemd/system/event-api.service
```

### Problém 6: SELinux blokuje přístup

**Řešení:**

```bash
# Zkontrolujte SELinux status
getenforce

# Pokud je Enforcing, zkuste dočasně nastavit na Permissive (pro test)
sudo setenforce 0

# Restart služby
sudo systemctl restart event-api

# Pokud to pomůže, nastavte SELinux pravidla správně
sudo setsebool -P httpd_can_network_connect 1
```

---

## 🔧 Kompletní diagnostika

Spusťte tyto příkazy pro kompletní diagnostiku:

```bash
# 1. Logy služby
echo "=== LOGY SLUŽBY ==="
sudo journalctl -u event-api -n 50 --no-pager

# 2. Stav služby
echo "=== STAV SLUŽBY ==="
sudo systemctl status event-api --no-pager

# 3. Kontrola service souboru
echo "=== SERVICE SOUBOR ==="
sudo cat /etc/systemd/system/event-api.service

# 4. Kontrola portu 80
echo "=== PORT 80 ==="
sudo lsof -i :80
sudo ss -tlnp | grep :80

# 5. Kontrola souborů
echo "=== SOUBORY ==="
ls -la /home/eventapi/event-api/
ls -la /home/eventapi/event-api/venv/bin/python*

# 6. Test ručního spuštění
echo "=== RUČNÍ TEST ==="
sudo su - eventapi -c "cd ~/event-api && source venv/bin/activate && python app.py" &
sleep 2
sudo pkill -f "python app.py"
```

---

## ✅ Rychlé řešení (zkuste postupně)

```bash
# 1. Zkontrolujte logy
sudo journalctl -u event-api -n 50

# 2. Zkontrolujte port 80
sudo lsof -i :80

# 3. Zkontrolujte capabilities
grep AmbientCapabilities /etc/systemd/system/event-api.service

# 4. Pokud chybí capabilities, přidejte je
sudo nano /etc/systemd/system/event-api.service
# Přidejte: AmbientCapabilities=CAP_NET_BIND_SERVICE

# 5. Nebo použijte setcap
sudo setcap 'cap_net_bind_service=+ep' /home/eventapi/event-api/venv/bin/python3

# 6. Reload a restart
sudo systemctl daemon-reload
sudo systemctl restart event-api

# 7. Zkontrolujte logy znovu
sudo journalctl -u event-api -n 50
```

---

## 📝 Testování bez systemd

Pro testování aplikace bez systemd:

```bash
# Přepněte se na uživatele
sudo su - eventapi

# Aktivujte venv
cd ~/event-api
source venv/bin/activate

# Spusťte aplikaci ručně (pro test použijte port 8000, ne 80)
PORT=8000 python app.py

# Pokud to funguje, problém je v systemd konfiguraci nebo portu 80
```

---

**Po zobrazení logů (`journalctl -u event-api -n 50`) uvidíte konkrétní chybovou zprávu, která vám řekne, co je špatně!**
