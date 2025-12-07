# Python verze a kompatibilita

## 📋 Požadavky na Python

Aplikace vyžaduje **Python 3.8 nebo vyšší** (doporučeno Python 3.11).

### Podporované verze

- ✅ **Python 3.11** - doporučeno (podle `runtime.txt` a `.python-version`)
- ✅ **Python 3.10** - plně podporováno
- ✅ **Python 3.9** - plně podporováno
- ✅ **Python 3.8** - minimální požadavek

### Konfigurační soubory

- **`.python-version`** - Python 3.11 (pro pyenv)
- **`runtime.txt`** - python-3.11.0 (pro Heroku/Railway)
- **`pyrightconfig.json`** - Python 3.11 (pro IDE type checking)

---

## 🔧 Nastavení pro různé platformy

### macOS

```bash
# Python 3.11 z Homebrew
brew install python@3.11

# Nebo použijte systémový Python 3.9+
python3 --version
```

### Linux (Ubuntu/Debian)

```bash
# Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# Nebo použijte systémový Python 3.9+
python3 --version
```

### Linux (CentOS/RHEL)

```bash
# Python 3.11 nebo použijte dostupnou verzi (3.9+)
dnf install python3 python3-pip python3-devel
python3 --version
```

### Windows

```bash
# Stáhněte Python 3.11 z python.org
# Nebo použijte Python 3.9+ z Microsoft Store
python --version
```

---

## ⚠️ Důležité poznámky

1. **Minimální verze**: Python 3.8+ (kvůli type hints a async/await)
2. **Doporučená verze**: Python 3.11 (pro nejlepší výkon a nové funkce)
3. **Kompatibilita**: Aplikace funguje na všech platformách (Windows, macOS, Linux)
4. **Virtualní prostředí**: Vždy používejte venv pro izolaci závislostí

---

## 🐍 Kontrola verze Pythonu

```bash
# Zkontrolujte verzi
python3 --version

# Nebo v Pythonu
python3 -c "import sys; print(sys.version)"
```

---

**Aplikace je kompatibilní s Pythonem 3.8+ na všech platformách!**
