# Návrh reorganizace struktury projektu

## 📁 Navrhovaná struktura

```
notda/
├── README.md                    # Hlavní README
├── .gitignore                   # Git ignore
├── requirements.txt             # Python závislosti
├── runtime.txt                  # Python runtime verze
├── Procfile                     # Pro Heroku/Railway
│
├── app.py                       # Hlavní aplikace
├── expose.py                    # Skript pro vystavení na internet
├── test_api.py                  # Testovací skript
│
├── docs/                        # 📚 Dokumentace
│   ├── README.md
│   ├── API_USAGE.md
│   ├── CENTOS_STREAM_10_DEPLOY.md
│   ├── SETUP_HTTPS.md
│   └── ...
│
├── scripts/                     # 🔧 Skripty
│   ├── deployment/              # Nasazovací skripty
│   │   ├── deploy_centos10.sh
│   │   ├── setup_centos_autostart.sh
│   │   └── centos_setup.sh
│   ├── development/             # Vývojářské skripty
│   │   ├── start.sh
│   │   ├── restart_server.sh
│   │   └── check_port.sh
│   └── tunneling/               # Tunnel skripty
│       ├── expose_cloudflare.sh
│       ├── restart_tunnel.sh
│       ├── switch_to_cloudflare.sh
│       └── get_url.sh
│
├── config/                      # ⚙️ Konfigurační soubory
│   ├── event-api.service        # Systemd service
│   └── nginx/                   # Nginx konfigurace (volitelné)
│       └── event-api.conf
│
├── tests/                       # 🧪 Testy
│   ├── test_api.py
│   └── test_version.sh
│
└── schemas/                     # 📋 API schémata
    └── Event-API-v20-SNAPSHOT.yaml
```

## 🎯 Výhody této struktury

1. **Lepší organizace** - související soubory jsou spolu
2. **Čistší kořen** - hlavní adresář obsahuje jen důležité soubory
3. **Snadnější navigace** - jasné rozdělení podle účelu
4. **Profesionálnější vzhled** - standardní struktura projektu

## 📝 Detaily reorganizace

### 1. Skripty (`scripts/`)

**Deployment skripty:**
- `deploy_centos10.sh` → `scripts/deployment/deploy_centos10.sh`
- `setup_centos_autostart.sh` → `scripts/deployment/setup_centos_autostart.sh`
- `centos_setup.sh` → `scripts/deployment/centos_setup.sh`

**Development skripty:**
- `start.sh` → `scripts/development/start.sh`
- `restart_server.sh` → `scripts/development/restart_server.sh`
- `check_port.sh` → `scripts/development/check_port.sh`

**Tunneling skripty:**
- `expose_cloudflare.sh` → `scripts/tunneling/expose_cloudflare.sh`
- `restart_tunnel.sh` → `scripts/tunneling/restart_tunnel.sh`
- `switch_to_cloudflare.sh` → `scripts/tunneling/switch_to_cloudflare.sh`
- `get_url.sh` → `scripts/tunneling/get_url.sh`

### 2. Konfigurační soubory (`config/`)

- `event-api.service` → `config/event-api.service`
- Vytvořit `config/nginx/` pro budoucí Nginx konfigurace

### 3. Testy (`tests/`)

- `test_api.py` → `tests/test_api.py`
- `test_version.sh` → `tests/test_version.sh`

### 4. Schémata (`schemas/`)

- `Event-API-v20-SNAPSHOT.yaml` → `schemas/Event-API-v20-SNAPSHOT.yaml`

## ⚠️ Co zůstane v kořeni

- `README.md` - hlavní dokumentace
- `app.py` - hlavní aplikace
- `expose.py` - skript pro vystavení
- `requirements.txt` - Python závislosti
- `runtime.txt` - Python runtime
- `Procfile` - pro Heroku/Railway
- `.gitignore` - Git konfigurace

## 🔄 Co bude potřeba aktualizovat

Po reorganizaci bude potřeba aktualizovat:

1. **Cesty v dokumentaci** - odkazy na skripty
2. **Systemd service** - cesta k aplikaci (pokud se změní)
3. **Deployment skripty** - cesty k souborům
4. **README.md** - odkazy na skripty

## 🚀 Postup reorganizace

1. Vytvořit složky
2. Přesunout soubory
3. Aktualizovat cesty v souborech
4. Aktualizovat dokumentaci
5. Otestovat, že vše funguje

---

**Chcete, abych provedl tuto reorganizaci?**
