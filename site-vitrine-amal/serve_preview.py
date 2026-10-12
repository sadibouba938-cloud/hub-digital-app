#!/usr/bin/env python3
"""Serveur de prévisualisation du site vitrine AMAL — Détergents du Sénégal.

Usage :
    python3 serve_preview.py            # http://0.0.0.0:8000
    python3 serve_preview.py 8080       # port personnalisé

Aucune dépendance : uniquement la bibliothèque standard Python.
Le site est 100 % statique (HTML / CSS / JS) — pour la mise en ligne définitive,
il suffit de déposer ce dossier chez n'importe quel hébergeur statique
(Netlify, Vercel, GitHub Pages, Hostinger, o2switch, cPanel…).

Points d'attention pour les aperçus distants (proxys, iframes) :
  * le serveur écoute sur 0.0.0.0 ;
  * il répond en HTTP/1.1 (le HTTP/1.0 par défaut de la bibliothèque standard
    referme la connexion à chaque requête et certains proxys n'affichent alors
    rien) ;
  * aucun contrôle d'en-tête « Host » ni d'origine : les domaines de
    prévisualisation sont acceptés tels quels ;
  * une sonde /healthz répond « ok » pour les contrôles de disponibilité ;
  * les journaux sont écrits sans mise en tampon.
"""
import http.server
import os
import socketserver
import sys
from functools import partial

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    # HTTP/1.1 : indispensable pour les proxys d'aperçu (connexions persistantes)
    protocol_version = "HTTP/1.1"
    # Les chemins servis restent dans ce dossier, même avec des liens symboliques
    follow_symlinks = True

    def do_GET(self):  # noqa: N802 (nom imposé par la bibliothèque standard)
        if self.path.split("?")[0] in ("/healthz", "/health"):
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        # Aperçu toujours à jour pendant la phase de validation
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, fmt, *args):  # journaux plus lisibles, écrits aussitôt
        sys.stderr.write("  %s\n" % (fmt % args))
        sys.stderr.flush()


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), partial(Handler, directory=DIRECTORY)) as httpd:
        print(f"🚀  AMAL — site vitrine servi sur http://0.0.0.0:{PORT}", flush=True)
        print(f"    Dossier : {DIRECTORY}", flush=True)
        print("    Appuyez sur Ctrl+C pour arrêter.", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur.", flush=True)
