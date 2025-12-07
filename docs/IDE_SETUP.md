# Nastavení IDE pro projekt

Tento dokument popisuje, jak nastavit IDE (VS Code, Cursor, PyCharm) pro správné rozpoznání importů.

---

## 🔧 Rychlé řešení

### 1. Vytvoření virtualního prostředí (pokud ještě neexistuje)

```bash
# Vytvoření venv
python3 -m venv venv

# Aktivace venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate     # Windows

# Instalace závislostí
pip install -r requirements.txt
```

### 2. Výběr Python interpretru v IDE

**VS Code / Cursor:**
1. Otevřete Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Zadejte: `Python: Select Interpreter`
3. Vyberte: `./venv/bin/python` (nebo `.\venv\Scripts\python.exe` na Windows)

**PyCharm:**
1. File → Settings → Project → Python Interpreter
2. Vyberte venv interpreter

---

## 📁 Konfigurační soubory

Projekt obsahuje následující konfigurační soubory:

### `pyrightconfig.json`
Konfigurace pro Pyright/Pylance (používá VS Code/Cursor).

### `.vscode/settings.json`
Nastavení VS Code/Cursor pro Python.

### `.python-version`
Verze Pythonu pro pyenv (volitelné).

---

## ✅ Ověření nastavení

Po nastavení by IDE mělo:
- ✅ Rozpoznat importy (`fastapi`, `pydantic`, atd.)
- ✅ Poskytovat autocomplete
- ✅ Zobrazovat type hints
- ✅ Nemělo by zobrazovat warningy o nerozpoznaných importech

---

## 🆘 Troubleshooting

### IDE stále nerozpoznává importy

1. **Zkontrolujte, že venv existuje:**
   ```bash
   ls -la venv/bin/python
   ```

2. **Zkontrolujte, že závislosti jsou nainstalované:**
   ```bash
   ./venv/bin/pip list | grep fastapi
   ```

3. **Restartujte IDE** - někdy je potřeba restartovat po změně konfigurace

4. **Zkontrolujte výstup terminálu IDE** - může obsahovat chybové zprávy

### Python interpreter není nalezen

```bash
# Zkontrolujte cestu k Pythonu v venv
ls -la venv/bin/python

# Pokud neexistuje, vytvořte venv znovu
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 Poznámky

- `venv/` je v `.gitignore`, takže každý vývojář si musí vytvořit vlastní venv
- Pro produkci se venv vytváří na serveru během nasazení
- Konfigurační soubory (`pyrightconfig.json`, `.vscode/settings.json`) jsou commitnuté do gitu

---

**Po správném nastavení by IDE mělo rozpoznat všechny importy bez warningů!**
