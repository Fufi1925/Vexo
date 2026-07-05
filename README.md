# 🚀 VEXO HUB — Deployment auf Railway.app

Dieses Repository ist 100% startklar für [Railway.app](https://railway.app/). Alle benötigten Konfigurationsdateien (`Procfile`, `railway.json` und `server.py`) sind bereits integriert!

---

## ⚡ So hostest du die Website in 3 Schritten auf Railway:

### Schritt 1: Auf GitHub hochladen (Push)
Lade dieses Repository in dein GitHub-Konto hoch:
```bash
git remote add origin https://github.com/DEIN-USER/vexo-hub.git
git branch -M main
git push -u origin main
```

### Schritt 2: Auf Railway neues Projekt erstellen
1. Gehe auf [railway.app](https://railway.app/) und logge dich mit GitHub ein.
2. Klicke oben rechts auf **"New Project"**.
3. Wähle **"Deploy from GitHub repo"** und wähle dein `vexo-hub` Repository aus.

### Schritt 3: Domain generieren & online gehen!
1. Railway erkennt die Konfiguration (`railway.json` & `Procfile`) automatisch und startet den Build-Prozess.
2. Klicke in Railway auf deine neu erstellte App -> **Settings** (oder **Networking**).
3. Klicke bei **Public Networking** auf **"Generate Domain"** (z. B. `vexo-hub-production.up.railway.app`).
4. **Fertig!** Deine VEXO-Website ist ab sofort 24/7 weltweit erreichbar! 🔥

---

## ⚙️ Technische Details (für Railway Einstellungen)

Falls du in Railway manuell Einstellungen prüfen oder eingeben möchtest:

* **Build Command:** *(leer lassen — kein Build nötig)*
* **Start Command:** `python3 server.py`
* **Root Directory:** `/`
* **Port:** Wird durch die Datei `server.py` automatisch über die von Railway vergebene `PORT` Variable gesteuert. Du musst keine zusätzlichen Port-Variablen setzen!
