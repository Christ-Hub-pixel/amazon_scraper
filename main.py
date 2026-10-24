"""Point d'entree du programme"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.controllers.scraping_controller import ScrapingController


def main():
    try:
        controller = ScrapingController()
        controller.demarrer()
    except KeyboardInterrupt:
        print("\nArret du programme.")
        sys.exit(0)


if __name__ == "__main__":
    main()
