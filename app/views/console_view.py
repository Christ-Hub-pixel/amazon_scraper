"""Vue pour l'interface console"""
from typing import List, Dict, Any
from app.models.produit import Produit


class ConsoleView:
    @staticmethod
    def afficher_banniere() -> None:
        print("=" * 60)
        print("         APPLICATION DE WEB SCRAPING - AMAZON")
        print("=" * 60)

    @staticmethod
    def afficher_menu() -> str:
        print("\n--- MENU ---")
        print("1. Lancer le scraping d'une categorie")
        print("2. Afficher les produits enregistres")
        print("3. Filtrer les produits par marque")
        print("4. Afficher les statistiques")
        print("5. Exporter les donnees en CSV")
        print("0. Quitter")
        return input("\nVotre choix : ").strip()

    @staticmethod
    def demander_parametres_scraping() -> tuple[str, int]:
        print("\n--- CHOIX DE LA CATÉGORIE TECH ---")
        print("  1. ecouteurs (Écouteurs / Casques)")
        print("  2. iphone (Smartphones Apple)")
        print("  3. asus (PC / Composants Asus)")
        print("  4. clavier gamer (Accessoires PC)")
        print("  Ou saisissez directement votre mot-clé.")
        saisie = input("Votre choix [1-4 ou mot-clé, défaut: ecouteurs] : ").strip()

        options = {
            "1": "ecouteurs",
            "2": "iphone",
            "3": "asus",
            "4": "clavier gamer"
        }
        mot_cle = options.get(saisie, saisie if saisie else "ecouteurs")

        nb_pages_str = input("Nombre de pages a scraper (recommandé: 3) [défaut: 3] : ").strip()
        try:
            nb_pages = int(nb_pages_str)
            if nb_pages < 1:
                nb_pages = 3
        except ValueError:
            nb_pages = 3

        return mot_cle, nb_pages

    @staticmethod
    def demander_marque() -> str:
        return input("Entrez la marque a filtrer (ex: iphone, sony, apple) : ").strip()

    @staticmethod
    def afficher_produits(produits: List[Produit]) -> None:
        if not produits:
            print("\nAucun produit trouve.")
            return

        print(f"\n--- LISTE DES PRODUITS ({len(produits)}) ---")
        print(f"{'N°':<4} | {'Marque':<12} | {'Prix':<10} | {'Titre'}")
        print("-" * 70)
        for idx, p in enumerate(produits, start=1):
            prix_str = f"{p.prix:.2f} €" if p.prix is not None else "N/A"
            titre_court = (p.titre[:45] + "...") if len(p.titre) > 48 else p.titre
            print(f"{idx:<4} | {p.marque:<12} | {prix_str:<10} | {titre_court}")
        print("-" * 70)

    @staticmethod
    def afficher_statistiques(stats: Dict[str, Any]) -> None:
        print("\n" + "=" * 50)
        print("           STATISTIQUES DE MARCHE")
        print("=" * 50)
        print(f"Total produits en base   : {stats.get('total_produits', 0)}")
        print(f"Produits avec prix       : {stats.get('nb_avec_prix', 0)}")
        print("-" * 50)
        print(f"1. Prix moyen            : {stats.get('prix_moyen', 0.0):.2f} €")
        print(f"2. Prix maximum          : {stats.get('prix_max', 0.0):.2f} €")
        print(f"   Prix minimum          : {stats.get('prix_min', 0.0):.2f} €")
        print("-" * 50)
        print("3. Nombre par categorie  :")
        par_cat = stats.get("par_categorie", {})
        if par_cat:
            for cat, count in par_cat.items():
                print(f"   - {cat:<20} : {count}")
        else:
            print("   (Aucune donnee)")
        print("=" * 50)

    @staticmethod
    def afficher_message(message: str) -> None:
        print(f"-> {message}")

    @staticmethod
    def afficher_erreur(message: str) -> None:
        print(f"[Erreur] {message}")
