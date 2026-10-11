#!/usr/bin/env python3
"""Serveur de prévisualisation du site vitrine Sunu Clean Sénégal.

Usage :
    python3 serve_preview.py            # http://0.0.0.0:8000
    python3 serve_preview.py 8080       # port personnalisé

Aucune dépendance : uniquement la bibliothèque standard Python.
Le site est 100 % statique (HTML / CSS / JS) — pour la mise en ligne définitive,
il suffit de déposer ce dossier chez n'importe quel hébergeur statique
(Netlify, Vercel, GitHub Pages, Hostinger, o2switch, cPanel…).
"""
import http.server
import os
import socketserver
import sys
from functools import partial

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Aperçu toujours à jour pendant la phase de validation
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):  # logs plus lisibles
        sys.stderr.write("  %s\n" % (fmt % args))


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), partial(Handler, directory=DIRECTORY)) as httpd:
    print(f"🚀  Sunu Clean — site vitrine servi sur http://0.0.0.0:{PORT}")
    print(f"    Dossier : {DIRECTORY}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
