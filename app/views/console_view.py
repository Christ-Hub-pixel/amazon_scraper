"""
Vue Console (ConsoleView) : gère l'interface utilisateur en console, l'affichage des étapes
du scraping, des produits extraits, du filtre par marque et des 3 statistiques d'étude de marché.
"""

from pathlib import Path
from typing import List

import config
from app.models.produit import Produit


class ConsoleView:
    """Classe POO dédiée à l'affichage et à l'interface console (MVC)."""

    LIGNE = "=" * 76

    def afficher_banniere(self, nb_pages_total: int, pause: float) -> None:
        """Affiche l'en-tête du programme au démarrage."""
        print(self.LIGNE)
        print(
            f"   AMAZON TECH SCRAPER v{config.VERSION} — ARCHITECTURE MVC & POO (SELENIUM)"
        )
        print(self.LIGNE)
        print(
            f"• Pagination      : {nb_pages_total} page(s) à scraper (PAGES_MAX = {config.PAGES_MAX})"
        )
        print(
            f"• Politesse       : pause de {pause:.1f}s (time.sleep) entre les requêtes"
        )
        print(f"• Timeout WebDriver: {config.TIMEOUT}s")
        print(self.LIGNE)

    def afficher_progression(
        self, categorie: str, page: int, nb_produits: int
    ) -> None:
        """Affiche l'avancement après chaque page scrapée."""
        print(
            f"[Scraping] Catégorie : '{categorie}' (Page {page}) "
            f"-> {nb_produits} produit(s) extrait(s)"
        )

    def afficher_aperçu_produits(
        self, produits: List[Produit], limite: int = 10
    ) -> None:
        """Affiche un aperçu des produits collectés (nom, prix, note, image, description)."""
        print("\n" + "-" * 76)
        print(
            f"APERÇU DES PRODUITS EXTRAITS ({min(len(produits), limite)} sur {len(produits)}) :"
        )
        print("-" * 76)
        for idx, produit in enumerate(produits[:limite], start=1):
            print(f"  {idx:2d}. {produit}")
            print(f"      Image : {produit.image}")
            print(f"      Desc. : {produit.description[:68]}...")

    def afficher_resultats_filtre(
        self, marque: str, produits_filtres: List[Produit]
    ) -> None:
        """Affiche les produits filtrés pour une marque spécifique (ex: 'iphone')."""
        print("\n" + "-" * 76)
        print(
            f"FILTRE PAR MARQUE : '{marque}' ({len(produits_filtres)} produit(s) trouvé(s))"
        )
        print("-" * 76)
        if not produits_filtres:
            print(f"  Aucun produit trouvé pour la marque '{marque}'.")
            return
        for idx, produit in enumerate(produits_filtres, start=1):
            print(f"  {idx:2d}. {produit}")

    def afficher_statistiques(self, stats: dict) -> None:
        """
        Affiche clairement les 3 statistiques demandées pour l'étude de marché :
        1. Moyenne
        2. Maximum
        3. Nombre par catégorie
        """
        print("\n" + self.LIGNE)
        print(
            "   STATISTIQUES ÉTUDE DE MARCHÉ (1. Moyenne | 2. Maximum | 3. Par catégorie)"
        )
        print(self.LIGNE)
        print(f"Total de produits collectés : {stats['total_produits']}")

        # Statistique 1 : Moyenne
        print("\n1. MOYENNE :")
        print(f"   • Prix moyen global  : {stats['prix_moyen']:.2f} €")
        if stats.get("note_moyenne"):
            print(f"   • Note moyenne       : {stats['note_moyenne']:.2f} / 5")

        # Statistique 2 : Maximum (et Minimum)
        produit_max = stats.get("produit_maximum")
        produit_min = stats.get("produit_minimum")
        print("\n2. MAXIMUM (ET MINIMUM) :")
        if produit_max:
            print(f"   • Prix maximum       : {stats['prix_maximum']:.2f} €")
            print(f"   • Produit le + cher  : {produit_max.titre}")
            print(f"   • Catégorie          : {produit_max.categorie}")
        if produit_min:
            print(
                f"   • Prix minimum       : {stats['prix_minimum']:.2f} € ({produit_min.titre})"
            )

        # Statistique 3 : Nombre par catégorie
        print("\n3. NOMBRE PAR CATÉGORIE :")
        details = stats.get("details_categories", {})
        for categorie, info in details.items():
            print(
                f"   • {categorie:<22} : {info['nb_produits']} produit(s) "
                f"| Moyenne: {info['prix_moyen']:7.2f} € | Max: {info['prix_max']:7.2f} €"
            )

        print(self.LIGNE)

    def afficher_confirmation_export(
        self,
        chemin_csv: Path,
        chemin_recap: Path,
        chemin_db: Path,
        chemin_json: Path,
    ) -> None:
        """Confirme l'enregistrement des fichiers CSV, SQLite et JSON."""
        print(f"✔ Export CSV global       : {chemin_csv}")
        print(f"✔ Récapitulatif catégories: {chemin_recap}")
        print(
            f"✔ Dossiers par catégorie  : {config.TECH_DIR}/<categorie>/data.csv & images/"
        )
        print(f"✔ Base de données SQLite  : {chemin_db}")
        print(f"✔ Cache JSON              : {chemin_json}")
        print(self.LIGNE)

    def afficher_menu_principal(self) -> str:
        """Affiche le menu de l'interface console interactive et retourne le choix."""
        print("\n" + self.LIGNE)
        print("   INTERFACE CONSOLE — MENU PRINCIPAL")
        print(self.LIGNE)
        print("  1. Afficher tous les produits scrapés")
        print("  2. Filtrer les produits par marque (ex: iphone, sony, asus)")
        print("  3. Afficher les statistiques de l'étude de marché")
        print("  4. Scraper une nouvelle catégorie technologique (avec pagination)")
        print("  5. Exporter en CSV et sauvegarder dans SQLite")
        print("  6. Lancer l'assistant vocal & IA J.A.R.V.I.S.")
        print("  0. Quitter")
        print("-" * 76)
        return input("Votre choix : ").strip()
