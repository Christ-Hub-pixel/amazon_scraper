"""
Contrôleur principal (ScrapingController) : coordonne le Scraper, le Modèle (Dépôt)
et les Vues (ConsoleView et ExportView) selon le patron d'architecture MVC.
"""

from pathlib import Path
from typing import List, Optional

import config
from app.models.depot import DepotProduits
from app.scraper.amazon_scraper import AmazonScraper
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView


class ScrapingController:
    """Contrôleur POO orchestrant le flux complet du projet de scraping."""

    def __init__(
        self,
        pause: float = config.DELAI_ENTRE_REQUETES,
        utiliser_selenium: bool = True,
    ) -> None:
        self.depot = DepotProduits()
        self.scraper = AmazonScraper(
            pause=pause,
            headless=config.HEADLESS,
            utiliser_selenium=utiliser_selenium,
        )
        self.console_view = ConsoleView()
        self.export_view = ExportView()

    def executer(
        self,
        categories: Optional[List[str]] = None,
        pages_par_categorie: int = 1,
        filtre_marque: Optional[str] = "iphone",
        chemin_csv: Path = config.FICHIER_EXPORT_CSV,
    ) -> DepotProduits:
        """
        Lance le pipeline complet :
        1. Télécharger et analyser au moins 3 pages (avec pagination et pause time.sleep)
        2. Stocker les objets Produit (nom, prix, image, description) dans le Dépôt
        3. Filtrer par marque (ex: 'iphone')
        4. Calculer et afficher les 3 statistiques (moyenne, maximum, nombre par catégorie)
        5. Enregistrer en CSV (exports/, data/tech/<cat>/data.csv & images, data/recap.csv) et SQLite
        """
        categories_cibles = categories or config.CATEGORIES_PAR_DEFAUT
        nb_pages_total = len(categories_cibles) * pages_par_categorie

        # Garantir au moins PAGES_MAX (3) pages scrapées
        if nb_pages_total < config.PAGES_MAX:
            pages_par_categorie = (config.PAGES_MAX // len(categories_cibles)) + 1
            nb_pages_total = len(categories_cibles) * pages_par_categorie

        self.console_view.afficher_banniere(
            nb_pages_total=nb_pages_total,
            pause=self.scraper.pause,
        )

        # Étapes 1 à 3 : Télécharger, Analyser et Extraire via Selenium + Sélecteurs CSS
        produits = self.scraper.scraper_categories(
            categories=categories_cibles,
            pages_par_categorie=pages_par_categorie,
            callback_progression=self.console_view.afficher_progression,
        )
        self.depot.ajouter_plusieurs(produits)

        # Aperçu des produits extraits
        self.console_view.afficher_aperçu_produits(self.depot.produits)

        # Filtre par marque (ex: "iphone")
        if filtre_marque:
            produits_marque = self.depot.filtrer_par_marque(filtre_marque)
            self.console_view.afficher_resultats_filtre(filtre_marque, produits_marque)

        # Affichage des 3 statistiques pour l'étude de marché
        statistiques = self.depot.obtenir_statistiques()
        self.console_view.afficher_statistiques(statistiques)

        # Étape 4 : Enregistrer en CSV, arborescence data/tech + images, recap.csv, SQLite et JSON
        self.sauvegarder_tout(chemin_csv=chemin_csv)

        return self.depot

    def sauvegarder_tout(
        self, chemin_csv: Path = config.FICHIER_EXPORT_CSV
    ) -> None:
        """Exporte toutes les données en CSV, dossiers d'images et base SQLite."""
        self.export_view.exporter_csv(self.depot.produits, chemin_csv)
        chemin_recap = self.export_view.exporter_arborescence_data(self.depot)
        chemin_db = self.depot.sauvegarder_sqlite(config.DB_PATH)
        chemin_json = self.depot.sauvegarder_json(config.FICHIER_CACHE_JSON)

        self.console_view.afficher_confirmation_export(
            chemin_csv=chemin_csv,
            chemin_recap=chemin_recap,
            chemin_db=chemin_db,
            chemin_json=chemin_json,
        )

    def lancer_menu_interactif(self) -> None:
        """Lance l'interface console interactive permettant de manipuler les données."""
        if len(self.depot) == 0:
            self.executer()

        while True:
            choix = self.console_view.afficher_menu_principal()
            if choix == "1":
                self.console_view.afficher_aperçu_produits(
                    self.depot.produits, limite=len(self.depot)
                )
            elif choix == "2":
                marque = input("Entrez la marque à filtrer (ex: iphone) : ").strip()
                resultats = self.depot.filtrer_par_marque(marque)
                self.console_view.afficher_resultats_filtre(marque, resultats)
            elif choix == "3":
                stats = self.depot.obtenir_statistiques()
                self.console_view.afficher_statistiques(stats)
            elif choix == "4":
                cat = input("Nouvelle catégorie tech à scraper : ").strip()
                nb_p_str = input("Nombre de pages à paginer [1] : ").strip()
                nb_p = int(nb_p_str) if nb_p_str.isdigit() and int(nb_p_str) > 0 else 1
                if cat:
                    nouveaux = self.scraper.scraper_categories(
                        categories=[cat],
                        pages_par_categorie=nb_p,
                        callback_progression=self.console_view.afficher_progression,
                    )
                    self.depot.ajouter_plusieurs(nouveaux)
                    self.sauvegarder_tout()
            elif choix == "5":
                self.sauvegarder_tout()
            elif choix == "6":
                from jarvis.assistant import JarvisAssistant

                assistant = JarvisAssistant(activer_voix=True)
                assistant.demarrer_session_interactive()
            elif choix == "0":
                print("Fermeture de l'application Amazon Scraper.")
                break
            else:
                print("Choix invalide, veuillez réessayer.")
