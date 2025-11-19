# Možnosti hostingu aplikace na internetu

Tento dokument popisuje různé možnosti hostingu vaší FastAPI aplikace na internetu.

## 📋 Požadavky aplikace

- Python 3.8+
- FastAPI framework
- Uvicorn ASGI server
- Port pro HTTP (standardně 8000, ale lze změnit)
- Možnost přijímat POST požadavky z externích systémů

---

## 🆓 Bezplatné možnosti

### 1. **Railway** ⭐ Doporučeno
- **URL**: https://railway.app
- **Cena**: Bezplatná tier s limity
- **Výhody**:
  - Velmi jednoduché nasazení (GitHub integrace)
  - Automatické SSL certifikáty
  - Generuje veřejnou URL
  - Podpora Python prostředí
  - Automatické restartování při změnách
- **Nevýhody**:
  - Po nečinnosti se aplikace může uspat (free tier)
- **Jak nasadit**:
  1. Vytvořte účet na Railway
  2. Připojte GitHub repository
  3. Railway automaticky detekuje Python projekt
  4. Nastavte `PORT` environment variable (Railway automaticky nastaví)
  5. Deploy!

### 2. **Render**
- **URL**: https://render.com
- **Cena**: Bezplatná tier s limity
- **Výhody**:
  - Jednoduché nasazení z GitHubu
  - Automatické SSL
  - Free tier s možností "sleep" po nečinnosti
- **Nevýhody**:
  - Aplikace se může uspat po 15 minutách nečinnosti (free tier)
- **Jak nasadit**:
  1. Vytvořte účet na Render
  2. Vytvořte nový "Web Service"
  3. Připojte GitHub repository
  4. Nastavte:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python3 app.py` nebo `uvicorn app:app --host 0.0.0.0 --port $PORT`
     - Environment: `PORT` (Render automaticky nastaví)

### 3. **Fly.io**
- **URL**: https://fly.io
- **Cena**: Bezplatná tier s limity
- **Výhody**:
  - Globální distribuce
  - Rychlé nasazení
  - CLI nástroj pro správu
- **Nevýhody**:
  - Vyžaduje CLI instalaci
  - Složitější setup než Railway/Render
- **Jak nasadit**:
  1. Nainstalujte Fly CLI: `curl -L https://fly.io/install.sh | sh`
  2. Přihlaste se: `fly auth login`
  3. Vytvořte aplikaci: `fly launch`
  4. Deploy: `fly deploy`

### 4. **PythonAnywhere**
- **URL**: https://www.pythonanywhere.com
- **Cena**: Bezplatná tier s limity
- **Výhody**:
  - Specializované na Python
  - Webové rozhraní pro správu
  - Jednoduché nasazení
- **Nevýhody**:
  - Omezené možnosti free tieru
  - Aplikace může být uspána po nečinnosti
- **Jak nasadit**:
  1. Vytvořte účet na PythonAnywhere
  2. Upload souborů přes webové rozhraní nebo Git
  3. Nastavte Web App s WSGI
  4. Konfigurujte start script

### 5. **Heroku** (již není free, ale stále populární)
- **URL**: https://www.heroku.com
- **Cena**: Placené (od $5/měsíc)
- **Výhody**:
  - Velmi jednoduché nasazení
  - Skvělé nástroje pro správu
  - Automatické SSL
- **Nevýhody**:
  - Už není bezplatná tier
- **Jak nasadit**:
  1. Vytvořte účet na Heroku
  2. Nainstalujte Heroku CLI
  3. `heroku create`
  4. `git push heroku main`

---

## 💰 Placené možnosti (produkční)

### 1. **DigitalOcean App Platform**
- **URL**: https://www.digitalocean.com/products/app-platform
- **Cena**: Od $5/měsíc
- **Výhody**:
  - Spolehlivé
  - Automatické SSL
  - Snadné škálování
  - GitHub integrace

### 2. **AWS (Elastic Beanstalk / EC2)**
- **URL**: https://aws.amazon.com
- **Cena**: Pay-as-you-go (obvykle $5-20/měsíc)
- **Výhody**:
  - Velmi škálovatelné
  - Spolehlivé
  - Mnoho možností konfigurace
- **Nevýhody**:
  - Složitější setup
  - Vyžaduje AWS znalosti

### 3. **Google Cloud Platform (Cloud Run)**
- **URL**: https://cloud.google.com/run
- **Cena**: Pay-as-you-go (obvykle $5-15/měsíc)
- **Výhody**:
  - Automatické škálování
  - Platíte jen za použití
  - Automatické SSL
- **Nevýhody**:
  - Složitější setup než managed řešení

### 4. **Azure App Service**
- **URL**: https://azure.microsoft.com/services/app-service
- **Cena**: Od $13/měsíc
- **Výhody**:
  - Enterprise-grade řešení
  - Automatické SSL
  - Snadné škálování

### 5. **VPS (Virtual Private Server)**
- **Poskytovatelé**: DigitalOcean Droplets, Linode, Vultr, Hetzner
- **Cena**: Od $4-6/měsíc
- **Výhody**:
  - Plná kontrola
  - Levné
  - Můžete hostovat více aplikací
- **Nevýhody**:
  - Vyžaduje server management
  - Musíte nastavit SSL sami (Let's Encrypt)
  - Musíte spravovat bezpečnost

---

## 🚀 Rychlý start - Railway (nejjednodušší)

### Krok 1: Připravte projekt pro Git
```bash
# Ujistěte se, že máte .gitignore
git init
git add .
git commit -m "Initial commit"
```

### Krok 2: Vytvořte Railway účet
1. Jděte na https://railway.app
2. Přihlaste se pomocí GitHubu
3. Klikněte na "New Project"
4. Vyberte "Deploy from GitHub repo"
5. Vyberte váš repository

### Krok 3: Railway automaticky:
- Detekuje Python projekt
- Nainstaluje závislosti z `requirements.txt`
- Spustí aplikaci
- Generuje veřejnou URL

### Krok 4: Nastavení environment variables (volitelné)
V Railway dashboardu můžete nastavit:
- `PORT` - Railway automaticky nastaví
- `API_KEY` - pokud chcete vlastní API klíč
- `HOST` - obvykle `0.0.0.0`

### Krok 5: Získejte URL
Railway automaticky vytvoří URL ve formátu:
```
https://your-app-name.up.railway.app
```

---

## 🔧 Úprava aplikace pro produkční prostředí

### 1. Upravte `app.py` pro produkční port:
```python
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Port z environment variable (hosting služby to nastaví)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Pro produkci použijte uvicorn s více workers
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        # Pro produkci můžete přidat:
        # workers=4  # Pro více worker procesů
    )
```

### 2. Vytvořte `Procfile` (pro Heroku/Railway):
```
web: python3 app.py
```
nebo
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

### 3. Vytvořte `runtime.txt` (volitelné, pro Python verzi):
```
python-3.11.0
```

---

## 📝 Checklist před nasazením

- [ ] Aplikace běží lokálně (`python3 app.py`)
- [ ] Všechny závislosti jsou v `requirements.txt`
- [ ] `.gitignore` obsahuje `__pycache__/`, `*.pyc`, `.env` atd.
- [ ] Environment variables jsou správně nastavené
- [ ] Port je konfigurovatelný přes `PORT` environment variable
- [ ] Host je nastaven na `0.0.0.0` (ne `localhost`)

---

## 🔒 Bezpečnostní poznámky

1. **API klíče**: Nikdy necommitujte API klíče do Gitu. Použijte environment variables.
2. **SSL**: Většina hosting služeb automaticky poskytuje SSL certifikáty.
3. **Rate limiting**: Zvažte přidání rate limitingu pro produkci.
4. **Logging**: Nastavte správné logování pro produkci.

---

## 🆘 Troubleshooting

### Aplikace se nespustí
- Zkontrolujte logy v hosting dashboardu
- Ověřte, že všechny závislosti jsou v `requirements.txt`
- Zkontrolujte, že port je správně nastaven

### Aplikace se uspává (free tier)
- Některé free tier služby uspávají aplikace po nečinnosti
- Zvažte upgrade na placený tier nebo použijte službu, která neuspává

### SSL certifikát nefunguje
- Většina služeb automaticky poskytuje SSL
- Pokud ne, použijte Let's Encrypt (pro VPS)

---

## 💡 Doporučení

**Pro rychlý start a testování:**
- **Railway** nebo **Render** - nejjednodušší nasazení

**Pro produkci s malým provozem:**
- **Railway** nebo **Render** (placený tier)
- **DigitalOcean App Platform**

**Pro větší provoz:**
- **AWS**, **GCP**, nebo **Azure**
- **VPS** s vlastním nastavením

**Pro úplnou kontrolu:**
- **VPS** (DigitalOcean, Hetzner, atd.)

---

## 📚 Užitečné odkazy

- Railway dokumentace: https://docs.railway.app
- Render dokumentace: https://render.com/docs
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/
- Uvicorn dokumentace: https://www.uvicorn.org/deployment/

