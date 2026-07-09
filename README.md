# 🚀 VEXO HUB — Deployment auf Railway.app

Dieses Repository ist 100% startklar für [Railway.app](https://railway.app/). Alle benötigten Konfigurationsdateien (`nixpacks.toml`, `.python-version`, `requirements.txt`, `Procfile`, `railway.json` und `server.py`) sind bereits integriert!

---

## 🛠️ Warum trat der Fehler `/bin/bash: line 1: python3: command not found` auf?
Railway nutzt für Builds den Container-Builder **Nixpacks**. Wenn in einem Repository nur eine `index.html` liegt und keine explizite Python-Konfiguration vorhanden ist, baut Nixpacks einen minimalen Container **ohne Python**. 

**Die Lösung:** Wir haben die Dateien `nixpacks.toml`, `.python-version` (3.11) und `requirements.txt` hinzugefügt. Dadurch wird Python 3 jetzt garantiert beim Build im Railway-Container installiert!

---

## ⚡ So aktualisierst du Railway jetzt (Fix anwenden):

### Schritt 1: Änderungen zu GitHub pushen
Öffne dein Terminal im Ordner `vexo` und pushe die neuen Dateien zu GitHub:
```bash
git push origin main
```
*(Da du die neuen Dateien jetzt im Repo hast, löst das auf Railway automatisch einen neuen, erfolgreichen Build aus!)*

---

### Schritt 2: Auf Railway prüfen
1. Gehe in dein Railway-Dashboard auf dein Projekt.
2. Der Build startet automatisch (oder klicke auf **Redeploy**).
3. Sobald der Build durch ist, läuft der Server sauber auf dem von Railway vergebenen Port!

---

## ⚙️ Technische Details (für Railway Einstellungen)

* **Build Engine:** Nixpacks (installiert automatisch Python 3 via `nixpacks.toml`)
* **Build Command:** *(leer lassen)*
* **Start Command:** `python3 server.py`
* **Root Directory:** `/`
