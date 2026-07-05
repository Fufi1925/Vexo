"""
VEXO HUB — Einfacher, robuster Webserver für Railway.app (Zero-Dependencies)
Liest automatisch die PORT-Umgebungsvariable von Railway aus.
"""
import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", 8080))

class VexoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Wenn nur die Haupt-URL (z. B. domain.com/) aufgerufen wird, index.html ausliefern
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    # Erlaube sofortiges Wiederverwenden des Ports (kein Address already in use)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), VexoHandler) as httpd:
        print(f"🚀 VEXO Hub ist online und läuft auf Port {PORT}")
        httpd.serve_forever()
