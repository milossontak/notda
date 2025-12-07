# Instalace Git na CentOS Stream 10

Pokud vidíte chybu `-bash: git: command not found`, potřebujete nainstalovat Git.

---

## 🚀 Rychlá instalace

```bash
# Jako root nebo s sudo
sudo dnf install -y git

# Ověření instalace
git --version
```

Mělo by zobrazit: `git version 2.x.x`

---

## 📝 Podrobný postup

### CentOS Stream 10 / Rocky Linux 10

```bash
# Aktualizace repozitářů
sudo dnf update -y

# Instalace Git
sudo dnf install -y git

# Ověření
git --version
```

### CentOS Stream 8/9 / Rocky Linux 8/9

```bash
sudo dnf install -y git
```

### CentOS 7

```bash
sudo yum install -y git
```

---

## ✅ Po instalaci Git

Po úspěšné instalaci Git můžete pokračovat v nasazení aplikace:

```bash
# Klonování repozitáře
git clone https://github.com/milossontak/notda.git event-api
cd event-api
```

---

## 🔍 Ověření, že Git funguje

```bash
# Zkontrolujte verzi
git --version

# Zkontrolujte konfiguraci
git config --global --list

# Pokud chcete nastavit jméno a email (volitelné)
git config --global user.name "Vaše jméno"
git config --global user.email "vas@email.com"
```

---

**Hotovo!** Nyní můžete pokračovat podle návodu v [CENTOS_STREAM_10_DEPLOY.md](CENTOS_STREAM_10_DEPLOY.md).
