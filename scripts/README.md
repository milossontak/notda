# Skripty

Tato složka obsahuje všechny pomocné skripty pro projekt.

## 📁 Struktura

### `deployment/` - Nasazovací skripty
Skripty pro nasazení aplikace na server:

- **`deploy_centos10.sh`** - Automatické nasazení na CentOS Stream 10 z GitHubu
- **`setup_centos_autostart.sh`** - Nastavení automatického spuštění po bootu
- **`centos_setup.sh`** - Základní setup prostředí na CentOS

### `development/` - Vývojářské skripty
Skripty pro lokální vývoj:

- **`start.sh`** - Spuštění aplikace
- **`restart_server.sh`** - Restart serveru
- **`check_port.sh`** - Kontrola, zda je port volný

### `tunneling/` - Tunnel skripty
Skripty pro vystavení aplikace na internet:

- **`expose_cloudflare.sh`** - Vystavení přes Cloudflare Tunnel
- **`restart_tunnel.sh`** - Restart tunnel služby
- **`switch_to_cloudflare.sh`** - Přepnutí na Cloudflare Tunnel
- **`get_url.sh`** - Získání aktuální URL

## 🚀 Použití

Všechny skripty jsou spustitelné přímo z jejich složky:

```bash
# Nasazení
./scripts/deployment/deploy_centos10.sh

# Vývoj
./scripts/development/start.sh

# Tunnel
./scripts/tunneling/expose_cloudflare.sh
```

Nebo z kořenového adresáře projektu:

```bash
bash scripts/deployment/deploy_centos10.sh
```
