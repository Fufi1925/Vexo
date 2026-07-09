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
}

# TikTok bietet KEINE kostenlose öffentliche Echtzeit-API für
# Follower- oder Live-Viewer-Zahlen. Um ECHTE, LIVE TikTok-Daten zu
# zeigen, hier eine echte Datenquelle eintragen (z.B. ein eigener Proxy,
# der mit einem gültigen TikTok-Token autorisiert ist und JSON der Form
# {"followers": N, "live_viewers": N, "live_now": bool} zurückgibt).
# Solange dies None ist, werden BEWUSST KEINE (fake) TikTok-Zahlen
# angezeigt.
TIKTOK_SOURCE = None


def fetch_tiktok():
    """Liefert echte TikTok-Daten oder None - niemals Fake-Zahlen."""
    if not TIKTOK_SOURCE:
        return None
    try:
        req = urllib.request.Request(
            TIKTOK_SOURCE, headers={"User-Agent": "VEXO-Hub/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.load(r)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Geo-Erkennung (nur Land, keine Speicherung der IP)
# ---------------------------------------------------------------------------
GEO_URL = "https://ipapi.co/{ip}/json/"

# Land -> Sprache (auto-detect). Deckt die haeufigsten Laender ab; alle
# 50 unterstuetzten Sprachen sind ueber SUPPORTED_LANGS im Frontend erreichbar.
# Unbekannte Laender -> "en" (Fallback).
COUNTRY_TO_LANG = {
    "DE": "de", "AT": "de", "CH": "de", "LI": "de", "LU": "de",
    "AD": "ca", "ES": "es", "MX": "es", "AR": "es", "CO": "es", "CL": "es",
    "PE": "es", "VE": "es", "EC": "es", "UY": "es", "BO": "es", "PY": "es",
    "CR": "es", "DO": "es", "GT": "es", "HN": "es", "SV": "es", "NI": "es",
    "PA": "es", "CU": "es", "PR": "es", "GQ": "es",
    "FR": "fr", "CA": "fr", "MC": "fr", "SN": "fr", "CI": "fr", "ML": "fr",
    "BF": "fr", "NE": "fr", "TG": "fr", "BJ": "fr", "CD": "fr", "CG": "fr",
    "GA": "fr", "CM": "fr", "CF": "fr", "TD": "fr", "GN": "fr", "MU": "fr",
    "IT": "it", "SM": "it", "VA": "it",
    "PT": "pt", "BR": "pt", "AO": "pt", "MZ": "pt", "GW": "pt", "CV": "pt", "ST": "pt",
    "NL": "nl", "SR": "nl", "AW": "nl",
    "EN": "en", "US": "en", "GB": "en", "AU": "en", "IE": "en", "NZ": "en",
    "ZA": "en", "KE": "en", "NG": "en", "GH": "en", "TZ": "en", "UG": "en",
    "ZM": "en", "ZW": "en", "ET": "en", "LK": "en", "SG": "en", "NA": "en",
    "BW": "en", "MW": "en", "JM": "en", "BS": "en", "BB": "en", "TT": "en",
    "IN": "hi", "JP": "ja", "KR": "ko", "CN": "zh", "TW": "zh", "HK": "zh", "MO": "zh",
    "RU": "ru", "BY": "ru", "KZ": "kk", "UZ": "ru",
    "AM": "am", "GE": "ka", "AZ": "az", "UA": "uk",
    "TR": "tr", "SA": "ar", "AE": "ar", "EG": "ar", "MA": "ar", "DZ": "ar",
    "TN": "ar", "IQ": "ar", "SY": "ar", "JO": "ar", "LB": "ar", "KW": "ar",
    "QA": "ar", "OM": "ar", "YE": "ar", "PS": "ar", "LY": "ar", "SD": "ar", "BH": "ar",
    "IR": "fa", "AF": "fa", "IL": "he", "PK": "ur", "BD": "bn",
    "TH": "th", "VN": "vi", "ID": "id", "MY": "ms", "PH": "fil",
    "PL": "pl", "CZ": "cs", "SK": "sk", "HU": "hu", "RO": "ro", "BG": "bg",
    "GR": "el", "CY": "el", "HR": "hr", "RS": "sr", "BA": "sr", "ME": "sr",
    "SI": "sl", "MK": "mk", "AL": "sq", "LT": "lt", "LV": "lv", "EE": "et",
    "FI": "fi", "SE": "sv", "NO": "no", "DK": "da", "IS": "en",
}

def geo_lookup(ip):
    """Bestimmt das Land aus der IP - ohne die IP zu loggen/speichern."""
    if not ip:
        return None
    try:
        url = GEO_URL.format(ip=ip)
        req = urllib.request.Request(url, headers={"User-Agent": "VEXO-Hub/1.0"})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.load(r)
        return data.get("country_code")
    except Exception:
        return None

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
    # Datenschutz: IP-Adressen werden NICHT geloggt
    def log_message(self, format, *args):
        return

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
        # JSON-API: Geo -> Sprache (ohne IP zu speichern)
        if self.path == "/api/geo":
            return self.serve_geo()
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
        discord = {}
        for key, code in CONFIG["discord_invites"].items():
            try:
                discord[key] = fetch_discord(code)
            except Exception:
                # Kein Fake-Fallback: bei Fehler keine Zahl zurückgeben
                discord[key] = {"name": "", "members": None, "online": None}
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "discord": discord,
            "tiktok": fetch_tiktok(),  # echte Daten oder None - nie Fake
        }
        return self._json(payload)

    def serve_visits(self):
        with visits_lock:
            n = load_visits() + 1
            save_visits(n)
        return self._json({"visits": n})

    def serve_geo(self):
        # IP wird NUR kurz zum Bestimmen des Landes genutzt - NIEMALS
        # geloggt oder persistent gespeichert (Datenschutz).
        ip = self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not ip:
            ip = self.client_address[0] if self.client_address else ""
        country = geo_lookup(ip)
        lang = COUNTRY_TO_LANG.get(country.upper(), "en") if country else "en"
        return self._json({"country": country, "lang": lang})


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), VexoHandler) as httpd:
        print(f"🚀 VEXO Hub ist online und läuft auf Port {PORT}")
        httpd.serve_forever()
