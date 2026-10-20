"""
Point d'entrée principal de l'application Amazon Scraper (Architecture MVC & POO).
Exécute le scraping d'au moins 3 pages avec Selenium, pause entre requêtes et timeouts,
enregistre en CSV + BD SQLite et affiche les 3 statistiques d'étude de marché.
"""

import argparse
import sys
from pathlib import Path

# Ajout automatique de .venv/lib/python*/site-packages si l'utilisateur lance
# `python3 main.py` sans avoir fait `source .venv/bin/activate` au préalable
_VENV_LIB = Path(__file__).resolve().parent / ".venv" / "lib"
if _VENV_LIB.exists():
    for _site_pkg in _VENV_LIB.glob("python*/site-packages"):
        if str(_site_pkg) not in sys.path:
            sys.path.insert(0, str(_site_pkg))

import config
from app.controllers.scraping_controller import ScrapingController


def analyser_arguments() -> argparse.Namespace:
    """Analyse les arguments optionnels passés en ligne de commande."""
    parser = argparse.ArgumentParser(
        description=f"Amazon Tech Scraper v{config.VERSION} (POO, MVC, Selenium, CSV & SQLite)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=config.CATEGORIES_PAR_DEFAUT,
        help="Liste des catégories technologiques à scraper (par défaut : 3 catégories).",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Nombre de pages de pagination à scraper par catégorie.",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=config.DELAI_ENTRE_REQUETES,
        help="Temps de pause (en secondes) entre deux requêtes (time.sleep).",
    )
    parser.add_argument(
        "--marque",
        type=str,
        default="iphone",
        help="Mot-clé de marque pour filtrer certains produits (ex: 'iphone').",
    )
    parser.add_argument(
        "--menu",
        action="store_true",
        help="Ouvrir l'interface console interactive après le scraping.",
    )
    parser.add_argument(
        "--sans-selenium",
        action="store_true",
        help="Mode rapide hors-ligne sans lancer le navigateur WebDriver.",
    )
    return parser.parse_args()


def main() -> None:
    """Fonction principale lançant le contrôleur de scraping."""
    args = analyser_arguments()
    controleur = ScrapingController(
        pause=args.pause,
        utiliser_selenium=not args.sans_selenium,
    )
    controleur.executer(
        categories=args.categories,
        pages_par_categorie=args.pages,
        filtre_marque=args.marque,
    )
    if args.menu:
        controleur.lancer_menu_interactif()


if __name__ == "__main__":
    main()
