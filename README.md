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

---

## 🎬 Echte TikTok-Live-Daten per Webhook / Proxy

TikTok bietet **keine** kostenlose Echtzeit-API. Um echte, live TikTok-Daten (Follower & Live-Status) zu zeigen, ohne je Fake-Zahlen zu erfinden, wird ein **eigener Proxy/Webhook** genutzt:

1. Du betreibst irgendwo einen kleinen Proxy/Dienst, der echte TikTok-Daten abruft.
2. Dieser sendet per **POST `/api/tiktok`** ein JSON an den VEXO-Server, z.B.:
   ```json
   {
     "username": "@ehvexo",
     "followers": 130500,
     "live_now": true,
     "live_viewers": 4200,
     "source": "myproxy"
   }
   ```
3. Der Server speichert das in `tiktok.json` und zeigt:
   - die **Follower** in der TikTok-Stat-Karte,
   - einen **🔴 LIVE-Badge** (im Bio-Panel + als floating Pill oben rechts) **nur wenn `live_now: true`**,
   - die echten **Live-Viewer** (falls mitgeschickt).

### Webhook absichern (optional, empfohlen)
Setze auf Railway eine Env-Variable `TIKTOK_WEBHOOK_SECRET` (oder `TIKTOK_WEBHOOK_SECRET`). Dann MUSS der Webhook das Secret übergeben:
```bash
curl -X POST https://deine-app.up.railway.app/api/tiktok \
  -H "X-Webhook-Secret: DEIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"live_now":true,"followers":130500,"live_viewers":4200}'
```
Ohne/mit falschem Secret → `401`. Ungültiges JSON → `400`.

### Alternative: Pull-Quelle
Statt Push kannst du `TIKTOK_SOURCE` auf eine URL setzen, die dasselbe JSON zurückgibt – der Server holt es sich bei jedem `/api/stats`-Aufruf.

---

## 📡 Live-Endpunkte & Datenschutz

| Endpoint | Funktion |
|----------|----------|
| `GET /api/stats` | Discord-Mitglieder + **Online** (echte Invite-API) + TikTok-Snapshot |
| `GET /api/visits` | Besucherzähler (persistent, ohne IP) |
| `GET /api/geo` | Land→Sprache (IP wird **nicht** geloggt/gespeichert) |
| `POST /api/tiktok` | TikTok-Webhook (siehe oben) |

**Regel:** Es werden **niemals Fake-Zahlen** angezeigt. Fehlen echte Daten (z.B. kein TikTok-Webhook), werden bewusst keine erfundenen Werte gezeigt – die Karte bleibt aus bzw. zeigt „Keine Live-Daten". IP-Adressen werden an keiner Stelle geloggt oder persistiert.
