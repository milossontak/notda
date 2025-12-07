# Bezpečnostní HTTP hlavičky

Aplikace implementuje následující bezpečnostní HTTP hlavičky pro zvýšení bezpečnosti.

---

## 🔒 Implementované hlavičky

### Content Security Policy (CSP)
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; ...
```

**Účel:** Omezuje, odkud mohou být načteny zdroje (skripty, styly, obrázky).

**Poznámka:** `unsafe-inline` a `unsafe-eval` jsou použity kvůli inline JavaScriptu v HTML stránce. Pro produkci zvažte přesunutí JS do externích souborů.

### Strict Transport Security (HSTS)
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Účel:** Vynucuje HTTPS připojení. Aktivní pouze při běhu na HTTPS.

**Nastavení:**
- `max-age=31536000` - 1 rok
- `includeSubDomains` - platí i pro subdomény
- `preload` - připraveno pro HSTS preload list

### X-Content-Type-Options
```
X-Content-Type-Options: nosniff
```

**Účel:** Zabraňuje prohlížeči v "sniffování" MIME typů.

### X-Frame-Options
```
X-Frame-Options: DENY
```

**Účel:** Zabraňuje zobrazení stránky v iframe (ochrana proti clickjacking).

**Poznámka:** CSP `frame-ancestors 'none'` má přednost, ale X-Frame-Options je zachován pro kompatibilitu se staršími prohlížeči.

### Referrer Policy
```
Referrer-Policy: strict-origin-when-cross-origin
```

**Účel:** Kontroluje, kolik informací o referreru se posílá při navigaci.

### X-XSS-Protection
```
X-XSS-Protection: 1; mode=block
```

**Účel:** Legacy hlavička pro starší prohlížeče (Chrome už ji ignoruje, ale některé nástroje ji očekávají).

### Permissions Policy
```
Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=(), usb=()
```

**Účel:** Zakazuje použití některých browser API.

---

## 📊 Bezpečnostní skóre

Po implementaci těchto hlaviček by mělo bezpečnostní skóre být:

- ✅ **Content Security Policy**: +25 bodů
- ✅ **Strict Transport Security**: +20 bodů (pouze na HTTPS)
- ✅ **X-Content-Type-Options**: +5 bodů
- ✅ **X-Frame-Options**: +20 bodů
- ✅ **Referrer Policy**: Bonus body

**Celkové zlepšení: +70 bodů**

---

## 🔧 Úprava CSP pro produkci

Pro produkci můžete zpřísnit CSP přesunutím inline JavaScriptu do externích souborů:

```python
# Přísnější CSP (bez unsafe-inline a unsafe-eval)
csp_policy = (
    "default-src 'self'; "
    "script-src 'self'; "  # Bez unsafe-inline
    "style-src 'self' 'unsafe-inline'; "  # CSS může zůstat inline
    "img-src 'self' data: blob:; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)
```

**Poznámka:** To vyžaduje přesunutí všech inline `<script>` tagů do externích `.js` souborů.

---

## 🧪 Testování

Po nasazení můžete otestovat hlavičky:

```bash
# Test hlaviček
curl -I https://your-domain.com

# Nebo podrobněji
curl -v https://your-domain.com 2>&1 | grep -i "content-security\|strict-transport\|x-content\|x-frame\|referrer"
```

---

## 📚 Reference

- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
- [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/)
- [Security Headers Test](https://securityheaders.com/)

---

**Všechny bezpečnostní hlavičky jsou automaticky přidávány všem HTTP odpovědím.**
