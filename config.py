"""Paramètres de configuration du projet"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
TECH_DATA_DIR = DATA_DIR / "tech"
EXPORT_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "scraping.db"
RECAP_CSV_PATH = DATA_DIR / "recap.csv"

AMAZON_URL = "https://www.amazon.fr/s?k="
HEADLESS = False
PAGES_MAX = 3
DELAI_ENTRE_REQUETES = 2.0
TIMEOUT = 10

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

# Création des dossiers nécessaires
DATA_DIR.mkdir(parents=True, exist_ok=True)
TECH_DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
