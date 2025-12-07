# Konfigurační soubory

Tato složka obsahuje konfigurační soubory pro různé prostředí.

## 📁 Soubory

### `event-api.service`
Systemd service soubor pro automatické spuštění aplikace po bootu na Linux serveru.

**Použití:**
```bash
# Zkopírování na server
sudo cp config/event-api.service /etc/systemd/system/event-api.service

# Úprava cest v souboru podle vašeho nasazení
sudo nano /etc/systemd/system/event-api.service

# Načtení a spuštění
sudo systemctl daemon-reload
sudo systemctl enable event-api
sudo systemctl start event-api
```

**Důležité:** Před použitím upravte cesty v souboru:
- `WorkingDirectory` - cesta k aplikaci
- `ExecStart` - cesta k Python binárce a app.py
- `Environment` - environment variables (PORT, HOST, API_KEY)

## 📝 Poznámky

- Service soubor je připraven pro běh na portu 8000
- Pro port 80 je potřeba přidat `AmbientCapabilities=CAP_NET_BIND_SERVICE`
- Viz [docs/CENTOS_STREAM_10_DEPLOY.md](../docs/CENTOS_STREAM_10_DEPLOY.md) pro podrobnosti
