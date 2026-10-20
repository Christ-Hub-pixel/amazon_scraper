#!/usr/bin/env python3
"""
Lanceur principal de J.A.R.V.I.S. (Assistant Vocal & IA).
Configure automatiquement l'environnement virtuel .venv et démarre Jarvis.
"""

import argparse
import sys
from pathlib import Path

# Auto-chargement des bibliothèques de .venv
_BASE_DIR = Path(__file__).resolve().parent
_VENV_LIB = _BASE_DIR / ".venv" / "lib"
if _VENV_LIB.exists():
    for _site_pkg in _VENV_LIB.glob("python*/site-packages"):
        if str(_site_pkg) not in sys.path:
            sys.path.insert(0, str(_site_pkg))

from jarvis.assistant import JarvisAssistant


def main() -> None:
    parser = argparse.ArgumentParser(
        description="J.A.R.V.I.S. — Assistant Vocal & IA (Système, Web & Amazon Scraper)"
    )
    parser.add_argument(
        "-c",
        "--commande",
        type=str,
        default=None,
        help="Exécuter une commande directement (ex: python3 jarvis.py -c 'diagnostic')",
    )
    parser.add_argument(
        "--muet",
        action="store_true",
        help="Désactiver la synthèse vocale (mode texte uniquement)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Lancer l'environnement virtuel interactif en HTML sur http://localhost:8080",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port du serveur Web HTML (par défaut : 8080)",
    )
    args = parser.parse_args()

    if args.web:
        from jarvis.web_server import lancer_serveur_web

        lancer_serveur_web(port=args.port)
        return

    assistant = JarvisAssistant(activer_voix=not args.muet)

    if args.commande:
        assistant.afficher_interface_accueil()
        reponse, _ = assistant.traiter_commande(args.commande)
        assistant.repondre(reponse)
    else:
        assistant.demarrer_session_interactive()


if __name__ == "__main__":
    main()

