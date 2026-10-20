# Amazon Scraper — Mini-Projet Web Scraping (POO & MVC)

Programme Python en **Programmation Orientée Objet (POO)** suivant l'architecture **MVC** permettant de récupérer les données de produits sur plusieurs pages, de les analyser avec **BeautifulSoup** et **Selenium**, de les enregistrer au format **CSV**, et d'afficher **3 statistiques** clés.

## Objectifs du Mini-Projet (Séance 2)

1. **Télécharger** : Récupérer le code HTML d'au moins **3 pages** (`Selenium` pour le contenu dynamique JavaScript / `requests`) en respectant les règles de politesse (`time.sleep` entre deux requêtes et `User-Agent` identifiable).
2. **Analyser** : Parcourir l'arbre HTML avec `BeautifulSoup`.
3. **Extraire** : Cibler les champs utiles via des **sélecteurs CSS** (`titre`, `prix`, `note`, `nb_avis`, `catégorie`, `url`).
4. **Enregistrer** : Exporter les produits dans un fichier CSV (`exports/produits_amazon.csv`).
5. **Statistiques** : Calculer et afficher dans la console :
   - **Moyenne** (prix moyen et note moyenne)
   - **Maximum** (prix maximum et produit le plus cher)
   - **Nombre par catégorie** (répartition des produits par catégorie)

## Architecture du Projet

```text
.
├── README.md
├── app
│   ├── __init__.py
│   ├── controllers
│   │   ├── __init__.py
│   │   └── scraping_controller.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── depot.py
│   │   └── produit.py
│   ├── scraper
│   │   ├── __init__.py
│   │   ├── amazon_scraper.py
│   │   ├── driver.py
│   │   └── parsing.py
│   └── views
│       ├── __init__.py
│       ├── console_view.py
│       └── export_view.py
├── config.py
├── data
├── exports
├── main.py
├── requirements.txt
└── tests
    └── __init__.py
```

## Installation

L'environnement virtuel `.venv` et toutes les dépendances (`selenium`, `beautifulsoup4`, `requests`, `webdriver-manager`, `lxml`) sont déjà installés dans le projet. Il suffit de l'activer :

```bash
source .venv/bin/activate
```

*(Si jamais vous devez recréer `.venv` sur Ubuntu sans `python3.14-venv`, utilisez `python3 -m venv --without-pip .venv`).*

## Exécution

Lancer le scraping par défaut (3 catégories = 3 pages avec pause entre chaque requête, export CSV + base SQLite + 3 statistiques) :

```bash
python3 main.py
```

Ouvrir le menu interactif en console :

```bash
python3 main.py --menu
```

Options disponibles :

```bash
# Personnaliser les catégories, le nombre de pages par catégorie, le filtre de marque ou la pause
python3 main.py --categories "ecouteurs" "ordinateur portable" "smartphone" --pages 1 --marque "iphone" --pause 2
```

