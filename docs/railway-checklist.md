# ✅ Checklist pro nasazení na Railway

## Co už máte připravené:

- ✅ **Procfile** - Railway ví, jak spustit aplikaci
- ✅ **requirements.txt** - všechny závislosti jsou definované
- ✅ **app.py** - správně nastavený PORT z environment variable
- ✅ **Git repository** - projekt je v gitu
- ✅ **.gitignore** - správně nastavený

## Rychlý postup nasazení:

### 1. Ověřte, že vše je v gitu:
```bash
git status
```

Pokud vidíte nějaké soubory jako "untracked", přidejte je:
```bash
git add Procfile requirements.txt app.py .gitignore
git commit -m "Připraveno pro Railway deployment"
```

### 2. Push na GitHub (pokud ještě není):
```bash
# Pokud ještě nemáte remote:
git remote add origin https://github.com/VÁŠ_USERNAME/VÁŠ_REPO.git
git push -u origin main
```

### 3. Nasazení na Railway:

1. Jděte na **https://railway.app**
2. Přihlaste se pomocí **GitHub**
3. Klikněte na **"New Project"**
4. Vyberte **"Deploy from GitHub repo"**
5. Vyberte váš repository
6. Railway automaticky:
   - Detekuje Python projekt
   - Nainstaluje závislosti
   - Spustí aplikaci podle Procfile
   - Vytvoří veřejnou URL

### 4. Nastavení Environment Variables (volitelné):

V Railway dashboardu můžete nastavit:
- `API_KEY` - pokud chcete vlastní API klíč (místo výchozího)
- `PORT` - Railway automaticky nastaví, nemusíte
- `HOST` - Railway automaticky nastaví na `0.0.0.0`, nemusíte

### 5. Získejte URL:

Railway automaticky vytvoří URL ve formátu:
```
https://your-app-name.up.railway.app
```

Tuto URL můžete použít pro:
- Webové rozhraní: `https://your-app-name.up.railway.app/`
- API volání: `https://your-app-name.up.railway.app/version`
- QR platby: `https://your-app-name.up.railway.app/qr-payment`

## Co Railway automaticky dělá:

✅ Detekuje Python projekt  
✅ Instaluje závislosti z `requirements.txt`  
✅ Spouští aplikaci podle `Procfile`  
✅ Nastaví `PORT` environment variable  
✅ Vytvoří HTTPS URL automaticky  
✅ Restartuje při push nových změn  

## Troubleshooting:

### Aplikace se nespustí:
- Zkontrolujte logy v Railway dashboardu
- Ověřte, že `Procfile` obsahuje: `web: python3 app.py`
- Zkontrolujte, že všechny závislosti jsou v `requirements.txt`

### Port chyba:
- Railway automaticky nastaví PORT, nemusíte nic dělat
- Aplikace už správně čte PORT z environment variable

### SSL/HTTPS:
- Railway automaticky poskytuje HTTPS certifikát
- URL je vždy HTTPS

## Další kroky po nasazení:

1. ✅ Otestujte webové rozhraní
2. ✅ Otestujte API endpointy
3. ✅ Nastavte vlastní API klíč (pokud chcete)
4. ✅ Sdílejte URL s externími systémy pro přijímání eventů

---

**Váš projekt je připravený! 🚀**

Stačí jen:
1. Push na GitHub (pokud ještě není)
2. Připojit repository na Railway
3. Deploy!

