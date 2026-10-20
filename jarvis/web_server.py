"""
Serveur Web local pour l'environnement virtuel HTML de J.A.R.V.I.S. & Amazon Scraper.
Permet de lancer l'interface HTML sur http://localhost:8080 et de relier le navigateur
au moteur Python (.venv, SQLite, ScrapingController et MoteurVocal).
"""

import json
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from jarvis.assistant import JarvisAssistant

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "interface_jarvis.html"


class JarvisHTTPHandler(BaseHTTPRequestHandler):
    """Gestionnaire HTTP servant l'interface HTML et l'API JSON en direct."""

    assistant = JarvisAssistant(activer_voix=True)

    def log_message(self, format: str, *args) -> None:
        pass

    def _send_json(self, data: dict, status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html", "/interface_jarvis.html"):
            if HTML_FILE.exists():
                content = HTML_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        if parsed.path == "/api/commande":
            qs = parse_qs(parsed.query)
            cmd = qs.get("q", [""])[0]
            reponse, _ = self.assistant.traiter_commande(cmd)
            self.assistant.voix.parler(reponse)
            self._send_json({"commande": cmd, "reponse": reponse})
            return

        self.send_error(404, "Ressource introuvable")


def lancer_serveur_web(port: int = 8080, ouvrir_navigateur: bool = True) -> None:
    """Démarre le serveur HTTP local pour l'interface HTML de Jarvis."""
    url = f"http://localhost:{port}"
    print("=" * 76)
    print(f"🌐 ENVIRONNEMENT VIRTUEL HTML J.A.R.V.I.S. ACTIF SUR : {url}")
    print(f"📄 Fichier HTML autonome : {HTML_FILE}")
    print("   Appuyez sur Ctrl+C pour arrêter le serveur.")
    print("=" * 76)

    if ouvrir_navigateur and shutil.which("xdg-open"):
        try:
            subprocess.Popen(
                ["xdg-open", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    serveur = HTTPServer(("0.0.0.0", port), JarvisHTTPHandler)
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur Web J.A.R.V.I.S.")
    finally:
        serveur.server_close()

