"""Paramètres de configuration globale du projet Amazon Scraper."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

AMAZON_URL = "https://www.amazon.fr"
HEADLESS = True
PAGES_MAX = 3
DELAI_ENTRE_REQUETES = 2.0
TIMEOUT = 10

DB_PATH = BASE_DIR / "data" / "amazon.db"
EXPORT_DIR = BASE_DIR / "exports"

# Paramètres complémentaires (dossiers data/tech, recap.csv et versionning)
VERSION = "1.0.0"
DATA_DIR = BASE_DIR / "data"
TECH_DIR = DATA_DIR / "tech"
RECAP_CSV_PATH = DATA_DIR / "recap.csv"
FICHIER_EXPORT_CSV = EXPORT_DIR / "produits_amazon.csv"

CATEGORIES_PAR_DEFAUT = [
    "ecouteurs",
    "ordinateur portable",
    "smartphone",
]

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Alias de compatibilité
BASE_URL = AMAZON_URL
SEARCH_URL = f"{AMAZON_URL}/s"
NB_PAGES_MIN = PAGES_MAX
PAUSE_ENTRE_REQUETES = DELAI_ENTRE_REQUETES
TIMEOUT_SELENIUM = TIMEOUT
EXPORTS_DIR = EXPORT_DIR
FICHIER_RECAP_CSV = RECAP_CSV_PATH
FICHIER_SQLITE_DB = DB_PATH
FICHIER_CACHE_JSON = DATA_DIR / "produits_cache.json"
