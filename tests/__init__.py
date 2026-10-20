"""
Tests unitaires du projet Amazon Scraper (Modèles, Statistiques, Filtre et Parsing).
Exécution : python3 -m unittest
"""

import unittest
from app.models.depot import DepotProduits
from app.models.produit import Produit
from app.scraper.amazon_scraper import AmazonScraper
from app.scraper.parsing import AmazonParser


class TestAmazonScraper(unittest.TestCase):
    """Vérifie le bon fonctionnement de la POO, des statistiques et du parsing HTML."""

    def setUp(self) -> None:
        self.depot = DepotProduits()
        self.p1 = Produit("Apple iPhone 15 128 Go", 869.00, "smartphone", note=4.6)
        self.p2 = Produit("Samsung Galaxy S24", 799.00, "smartphone", note=4.5)
        self.p3 = Produit("Sony WF-1000XM5", 219.99, "ecouteurs", note=4.4)
        self.depot.ajouter_plusieurs([self.p1, self.p2, self.p3])

    def test_statistiques_mini_projet(self) -> None:
        """Teste les 3 statistiques : moyenne, maximum et nombre par catégorie."""
        stats = self.depot.obtenir_statistiques()
        self.assertEqual(stats["total_produits"], 3)
        self.assertAlmostEqual(stats["prix_moyen"], 629.33, places=2)
        self.assertEqual(stats["prix_maximum"], 869.00)
        self.assertEqual(stats["nombre_par_categorie"]["smartphone"], 2)
        self.assertEqual(stats["nombre_par_categorie"]["ecouteurs"], 1)

    def test_filtre_par_marque_iphone(self) -> None:
        """Teste que le filtre 'iphone' ne retourne que les produits iPhone."""
        iphones = self.depot.filtrer_par_marque("iphone")
        self.assertEqual(len(iphones), 1)
        self.assertIn("iPhone", iphones[0].titre)

    def test_parsing_html(self) -> None:
        """Teste l'extraction des produits et de la pagination depuis l'arbre HTML."""
        scraper = AmazonScraper(pause=0.0, utiliser_selenium=False)
        parser = AmazonParser()
        html = scraper._generer_html_secours("ecouteurs", page=1)
        produits = parser.extraire_produits(html, categorie="ecouteurs")
        self.assertGreaterEqual(len(produits), 5)
        self.assertTrue(all(p.prix > 0 for p in produits))
        self.assertIsNotNone(parser.trouver_page_suivante(html))


if __name__ == "__main__":
    unittest.main()
