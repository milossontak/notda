# Řešení problému s instalací Pythonu 3.11 na CentOS

Pokud se vám zobrazí chyba `No match for argument: python311`, použijte tento návod.

---

## 🔍 Krok 1: Zjištění verze CentOS

```bash
cat /etc/redhat-release
# nebo
cat /etc/os-release
```

---

## ✅ Řešení podle verze CentOS

### CentOS Stream 8/9 nebo Rocky Linux 8/9

Na těchto verzích použijte Python 3.9 nebo 3.10, které jsou dostupné ve výchozích repozitářích:

```bash
# Instalace Pythonu 3.9 (nebo 3.10, pokud je dostupný)
sudo dnf install -y python39 python39-pip python39-devel gcc libjpeg-devel zlib-devel

# Nebo zkuste Python 3.10
sudo dnf install -y python310 python310-pip python310-devel gcc libjpeg-devel zlib-devel

# Nebo použijte python3 (obvykle Python 3.9+)
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel
```

**Ověření:**
```bash
python3.9 --version
# nebo
python3.10 --version
# nebo
python3 --version
```

### CentOS Stream 10 nebo novější

Na CentOS Stream 10 použijte Python 3.12 nebo python3:

```bash
# Zkuste Python 3.12
sudo dnf install -y python3.12 python3.12-pip python3.12-devel gcc libjpeg-devel zlib-devel

# Nebo použijte python3 (obvykle nejnovější dostupná verze)
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel
```

### CentOS 7

Na CentOS 7 použijte Software Collections (SCL):

```bash
# Instalace SCL
sudo yum install -y centos-release-scl

# Instalace Pythonu 3.9 z SCL
sudo yum install -y rh-python39 rh-python39-python-devel gcc libjpeg-devel zlib-devel

# Aktivace Pythonu 3.9
scl enable rh-python39 bash

# Ověření
python3 --version
```

---

## 🐍 Alternativa: Kompilace Pythonu 3.11 ze zdrojů

Pokud skutečně potřebujete Python 3.11, můžete ho zkompilovat ze zdrojů:

```bash
# Instalace build dependencies
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel xz-devel

# Stažení Pythonu 3.11
cd /tmp
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
tar xzf Python-3.11.0.tgz
cd Python-3.11.0

# Konfigurace a kompilace
./configure --enable-optimizations --prefix=/usr/local
make -j$(nproc)
sudo make altinstall

# Vytvoření symlinku
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11

# Ověření
python3.11 --version
pip3.11 --version
```

---

## ✅ Doporučené řešení (nejjednodušší)

**Pro většinu případů stačí použít dostupnou verzi Pythonu 3.9+:**

```bash
# Zkuste nejprve python3 (obvykle Python 3.9+)
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel

# Ověření verze
python3 --version

# Pokud je Python 3.8+, můžete pokračovat
```

**Aplikace funguje s Pythonem 3.8+, takže Python 3.9 nebo 3.10 je dostačující!**

---

## 🔧 Úprava dalších kroků

Pokud použijete jinou verzi Pythonu než 3.11, upravte příkazy:

**Místo:**
```bash
python3.11 -m venv venv
```

**Použijte:**
```bash
python3.9 -m venv venv
# nebo
python3 -m venv venv
```

**A v systemd service souboru upravte cestu:**
```ini
ExecStart=/home/eventapi/event-api/venv/bin/python /home/eventapi/event-api/app.py
```

(Python v venv bude automaticky správná verze)

---

## 📝 Rychlý fix pro váš případ

Zkuste tento příkaz (pro CentOS Stream 10):

```bash
# Instalace Pythonu 3.12 nebo python3
sudo dnf install -y python3.12 python3.12-pip python3.12-devel gcc libjpeg-devel zlib-devel

# Nebo jednoduše
sudo dnf install -y python3 python3-pip python3-devel gcc libjpeg-devel zlib-devel

# Ověření
python3 --version
```

Pokud je verze Pythonu 3.8 nebo vyšší, můžete pokračovat podle návodu!
