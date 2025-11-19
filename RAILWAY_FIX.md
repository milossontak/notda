# Oprava buildu na Railway

## Problém
Railway selhal při instalaci závislostí s chybou:
```
ERROR: failed to build: failed to solve: process "pip install -r requirements.txt" did not complete successfully: exit code: 1
```

## Řešení

### 1. Opravený requirements.txt

Problém byl v syntaxi `qrcode[pil]==7.4.2`. Railway někdy má problémy s extra dependencies v hranatých závorkách.

**Opraveno na:**
```
qrcode==7.4.2
Pillow==10.1.0
```

### 2. Přidán runtime.txt

Specifikuje Python verzi pro Railway:
```
python-3.11.0
```

### 3. Commit a push změn

```bash
git add requirements.txt runtime.txt
git commit -m "Fix Railway build - split qrcode[pil] to separate packages"
git push
```

Railway automaticky znovu spustí build po push.

## Alternativní řešení (pokud problém přetrvá)

### Možnost 1: Použít buildpacks

V Railway dashboardu můžete nastavit buildpack:
- Settings → Build → Build Command: `pip install --upgrade pip && pip install -r requirements.txt`

### Možnost 2: Vytvořit build script

Vytvořte `build.sh`:
```bash
#!/bin/bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

A v Railway nastavte Build Command na: `bash build.sh`

### Možnost 3: Zkontrolovat logy

V Railway dashboardu:
1. Jděte na vaši službu
2. Klikněte na "Deployments"
3. Klikněte na failed deployment
4. Podívejte se na "Build Logs" pro detailní chybovou hlášku

## Ověření

Po úspěšném buildu by mělo být vidět:
- ✅ Build successful
- ✅ Service running
- ✅ Veřejná URL dostupná

## Kontakt

Pokud problém přetrvá, pošlete:
1. Celý build log z Railway
2. Verzi Python na Railway (mělo by být 3.11 podle runtime.txt)

