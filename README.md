# Projet de Web Scraping - Amazon

Projet réalisé dans le cadre du cours de Programmation Python (Séance Web Scraping).

L'application permet d'extraire des données de produits sur Amazon en utilisant Selenium, de gérer la pagination, de sauvegarder les résultats dans une base SQLite et sous forme de fichiers CSV, et de calculer des statistiques pour une étude de marché.

## Structure du projet

Le projet respecte une architecture MVC :

```text
web_scraping/
├── app/
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── scraping_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── depot.py
│   │   └── produit.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── amazon_scraper.py
│   │   ├── driver.py
│   │   └── parsing.py
│   └── views/
│       ├── __init__.py
│       ├── console_view.py
│       └── export_view.py
├── config.py
├── data/
│   ├── tech/
│   └── recap.csv
├── exports/
├── tests/
│   └── __init__.py
├── main.py
└── requirements.txt
```

## Fonctionnalités

- Scraping de pages Amazon avec Selenium WebDriver.
- Gestion de la pagination (3 pages minimum).
- Respect des règles de politesse (pause entre les requêtes).
- Téléchargement et stockage des images dans `data/tech/<categorie>/images/`.
- Stockage des données dans `data/tech/<categorie>/data.csv` et dans une base SQLite (`data/scraping.db`).
- Mise à jour du fichier récapitulatif `data/recap.csv`.
- Filtrage des produits par marque (ex: iPhone, Samsung).
- Calcul de 3 statistiques : prix moyen, prix maximum et nombre de produits par catégorie.

## Installation et exécution

1. Créer et activer l'environnement virtuel :

```bash
python -m venv .venv
# Sur Windows :
.\.venv\Scripts\activate
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Lancer le programme :

```bash
python main.py
```
