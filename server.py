"""
VEXO HUB - Webserver für Railway.app (Zero-Dependencies)
Liest automatisch die PORT-Umgebungsvariable von Railway aus.

Zusätzlich zu den statischen Dateien liefert dieser Server zwei
JSON-Endpunkte:
  /api/stats  -> Live-Daten von Discord (Mitgliederzahlen) + TikTok-Konfig
  /api/visits -> Zählt und gibt die Gesamtzahl der Website-Aufrufe zurück
"""
import http.server
import socketserver
import os
import json
import threading
import urllib.request
from datetime import datetime, timezone

PORT = int(os.environ.get("PORT", 8080))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VISITS_FILE = os.path.join(BASE_DIR, "visits.json")
visits_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Konfiguration / Fallback-Werte
# ---------------------------------------------------------------------------
CONFIG = {
    # Discord-Einladungscodes (wie in index.html verlinkt)
    "discord_invites": {
        "fuseEh": "U2XGV5jaAr",
        "voidShop": "h83FkGxhps",
        "community": "39dqMvXCnc",
    },
    # Fallback, falls die Discord-API nicht erreichbar ist oder ein
    # Invite abgelaufen ist. TikTok-Zahlen sind Konfig-Werte, da TikTok
    # keine kostenlose Echtzeit-API für Follower/Live-Viewer anbietet.
    "fallback": {
        "fuseEh_members": 1850,
        "voidShop_members": 500,
        "community_members": 1200,
        "tiktok_followers": 128400,
        "tiktok_views": 2450000,
        "tiktok_live_viewers": 0,
        "tiktok_live_now": False,
    },
}

# ---------------------------------------------------------------------------
# Besucherzähler (persistent in visits.json)
# ---------------------------------------------------------------------------
def load_visits():
    try:
        with open(VISITS_FILE) as f:
            return int(json.load(f).get("count", 0))
    except Exception:
        return 0

def save_visits(n):
    try:
        with open(VISITS_FILE, "w") as f:
            json.dump({"count": n}, f)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Discord-Daten live abrufen (offizielle, kostenlose Invite-API)
# ---------------------------------------------------------------------------
def fetch_discord(code):
    url = f"https://discord.com/api/v10/invites/{code}?with_counts=true"
    req = urllib.request.Request(url, headers={"User-Agent": "VEXO-Hub/1.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.load(r)
    return {
        "name": (data.get("guild") or {}).get("name", ""),
        "members": data.get("approximate_member_count", 0) or 0,
        "online": data.get("approximate_presence_count", 0) or 0,
    }

# ---------------------------------------------------------------------------
# HTTP-Handler
# ---------------------------------------------------------------------------
class VexoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Hauptseite ausliefern
        if self.path in ("/", ""):
            self.path = "/index.html"
        # JSON-API: Live-Statistiken
        if self.path == "/api/stats":
            return self.serve_stats()
        # JSON-API: Besucherzähler
        if self.path == "/api/visits":
            return self.serve_visits()
        return super().do_GET()

    def _json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_stats(self):
        fb = CONFIG["fallback"]
        discord = {}
        for key, code in CONFIG["discord_invites"].items():
            try:
                discord[key] = fetch_discord(code)
            except Exception:
                discord[key] = {
                    "name": "",
                    "members": fb.get(key + "_members", 0),
                    "online": 0,
                }
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "discord": discord,
            "tiktok": {
                "followers": fb["tiktok_followers"],
                "views": fb["tiktok_views"],
                "live_viewers": fb["tiktok_live_viewers"],
                "live_now": fb["tiktok_live_now"],
            },
        }
        return self._json(payload)

    def serve_visits(self):
        with visits_lock:
            n = load_visits() + 1
            save_visits(n)
        return self._json({"visits": n})


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), VexoHandler) as httpd:
        print(f"🚀 VEXO Hub ist online und läuft auf Port {PORT}")
        httpd.serve_forever()
