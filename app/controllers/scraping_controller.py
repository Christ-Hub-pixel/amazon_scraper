"""Controleur principal (MVC)"""
from typing import List, Optional
from app.models.depot import Depot
from app.models.produit import Produit
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView
from app.scraper.amazon_scraper import AmazonScraper


class ScrapingController:
    def __init__(self):
        self.depot = Depot()
        self.view = ConsoleView()
        self.export_view = ExportView()
        self.derniers_produits: List[Produit] = []
        self.derniere_categorie: str = "technologies"

    def demarrer(self) -> None:
        self.view.afficher_banniere()

        try:
            while True:
                choix = self.view.afficher_menu()

                if choix == "1":
                    self.action_scraper()
                elif choix == "2":
                    self.action_afficher_tous()
                elif choix == "3":
                    self.action_filtrer_marque()
                elif choix == "4":
                    self.action_afficher_statistiques()
                elif choix == "5":
                    self.action_exporter()
                elif choix == "0":
                    self.view.afficher_message("Au revoir.")
                    break
                else:
                    self.view.afficher_erreur("Choix invalide.")
        except KeyboardInterrupt:
            self.view.afficher_message("\nInterruption utilisateur reçue. Fermeture propre...")

    def action_scraper(self) -> None:
        mot_cle, nb_pages = self.view.demander_parametres_scraping()
        self.derniere_categorie = mot_cle

        self.view.afficher_message(f"Lancement du scraping pour '{mot_cle}' ({nb_pages} pages)...")

        scraper: Optional[AmazonScraper] = None
        try:
            scraper = AmazonScraper()
            produits = scraper.scraper_categorie(
                mot_cle=mot_cle,
                nb_pages=nb_pages,
                telecharger_images=True
            )

            if not produits:
                self.view.afficher_erreur("Aucun produit extrait.")
                return

            self.derniers_produits = produits

            # Sauvegarde en base SQLite
            nb_sauvegardes = self.depot.sauvegarder_produits(produits)
            self.view.afficher_message(f"{nb_sauvegardes} produits sauvegardes dans la base SQLite.")

            # Sauvegarde dans data/tech/<categorie>/data.csv
            chemin_csv = self.export_view.exporter_categorie_csv(produits, mot_cle)
            self.view.afficher_message(f"Fichier CSV genere : {chemin_csv}")

            # Mise a jour de recap.csv
            prix_valides = [p.prix for p in produits if p.prix is not None]
            prix_moyen = round(sum(prix_valides) / len(prix_valides), 2) if prix_valides else 0.0
            prix_max = max(prix_valides) if prix_valides else 0.0

            chemin_recap = self.export_view.mettre_a_jour_recap({
                "categorie": mot_cle,
                "nb_produits": len(produits),
                "prix_moyen": prix_moyen,
                "prix_max": prix_max
            })
            self.view.afficher_message(f"Fichier recap mis a jour : {chemin_recap}")

        except Exception as e:
            self.view.afficher_erreur(f"Erreur durant le scraping : {e}")
        finally:
            if scraper:
                scraper.fermer()

    def action_afficher_tous(self) -> None:
        produits = self.depot.obtenir_tous()
        self.view.afficher_produits(produits)

    def action_filtrer_marque(self) -> None:
        marque = self.view.demander_marque()
        if not marque:
            self.view.afficher_erreur("Marque vide.")
            return

        produits = self.depot.filtrer_par_marque(marque)
        self.view.afficher_message(f"Produits trouves pour '{marque}' :")
        self.view.afficher_produits(produits)

    def action_afficher_statistiques(self) -> None:
        stats = self.depot.calculer_statistiques()
        self.view.afficher_statistiques(stats)

    def action_exporter(self) -> None:
        produits = self.depot.obtenir_tous()
        if not produits:
            self.view.afficher_erreur("Aucune donnee a exporter.")
            return

        chemin = self.export_view.exporter_general_csv(produits, "tous_les_produits.csv")
        self.view.afficher_message(f"Donnees exportees : {chemin}")
