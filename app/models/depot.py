"""
Modèle Dépôt (Repository) gérant la collection de produits, le filtrage par marque,
la persistance SQLite/JSON et le calcul des 3 statistiques pour l'étude de marché.
"""

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

from app.models.produit import Produit


class DepotProduits:
    """Gère le stockage des produits scrapés, les filtres et les statistiques."""

    def __init__(self) -> None:
        self._produits: List[Produit] = []

    def ajouter(self, produit: Produit) -> None:
        """Ajoute un produit au dépôt s'il a un prix valide (> 0)."""
        if produit and produit.prix > 0:
            self._produits.append(produit)

    def ajouter_plusieurs(self, produits: List[Produit]) -> None:
        """Ajoute une liste de produits au dépôt."""
        for produit in produits:
            self.ajouter(produit)

    @property
    def produits(self) -> List[Produit]:
        """Retourne la liste de tous les produits enregistrés."""
        return list(self._produits)

    def __len__(self) -> int:
        return len(self._produits)

    def filtrer_par_marque(self, marque: str) -> List[Produit]:
        """
        Filtre les produits selon une marque ou un mot-clé (ex: 'iphone', 'sony', 'asus').
        """
        if not marque or not marque.strip():
            return self.produits
        return [p for p in self._produits if p.correspond_marque(marque)]

    def filtrer_par_categorie(self, categorie: str) -> List[Produit]:
        """Retourne uniquement les produits appartenant à une catégorie donnée."""
        cible = categorie.strip().lower()
        return [p for p in self._produits if p.categorie.lower() == cible]

    def calculer_prix_moyen(self, produits: Optional[List[Produit]] = None) -> float:
        """Statistique 1 : Calcule la moyenne des prix des produits."""
        cible = self._produits if produits is None else produits
        if not cible:
            return 0.0
        total = sum(p.prix for p in cible)
        return round(total / len(cible), 2)

    def trouver_produit_max(
        self, produits: Optional[List[Produit]] = None
    ) -> Optional[Produit]:
        """Statistique 2 : Trouve le produit ayant le prix maximum."""
        cible = self._produits if produits is None else produits
        if not cible:
            return None
        return max(cible, key=lambda p: p.prix)

    def trouver_produit_min(
        self, produits: Optional[List[Produit]] = None
    ) -> Optional[Produit]:
        """Trouve le produit ayant le prix minimum (utile pour l'étude de marché)."""
        cible = self._produits if produits is None else produits
        if not cible:
            return None
        return min(cible, key=lambda p: p.prix)

    def compter_par_categorie(self) -> Dict[str, int]:
        """Statistique 3 : Compte le nombre de produits par catégorie."""
        compteur = Counter(p.categorie for p in self._produits)
        return dict(compteur)

    def obtenir_statistiques(self) -> dict:
        """
        Retourne un résumé complet contenant les 3 statistiques exigées par le mini-projet :
        1. Moyenne des prix (et note moyenne)
        2. Maximum (prix max et produit associé)
        3. Nombre par catégorie (avec détails pour l'étude de marché)
        """
        produit_max = self.trouver_produit_max()
        produit_min = self.trouver_produit_min()
        notes_valides = [p.note for p in self._produits if p.note is not None]
        note_moyenne = (
            round(sum(notes_valides) / len(notes_valides), 2) if notes_valides else 0.0
        )

        repartition = self.compter_par_categorie()
        details_categories = {}
        for cat in repartition:
            prods_cat = self.filtrer_par_categorie(cat)
            p_max = self.trouver_produit_max(prods_cat)
            p_min = self.trouver_produit_min(prods_cat)
            details_categories[cat] = {
                "nb_produits": len(prods_cat),
                "prix_moyen": self.calculer_prix_moyen(prods_cat),
                "prix_max": p_max.prix if p_max else 0.0,
                "prix_min": p_min.prix if p_min else 0.0,
            }

        return {
            "total_produits": len(self._produits),
            "prix_moyen": self.calculer_prix_moyen(),
            "prix_maximum": produit_max.prix if produit_max else 0.0,
            "produit_maximum": produit_max,
            "prix_minimum": produit_min.prix if produit_min else 0.0,
            "produit_minimum": produit_min,
            "note_moyenne": note_moyenne,
            "nombre_par_categorie": repartition,
            "details_categories": details_categories,
        }

    def sauvegarder_json(self, chemin_fichier: Path) -> Path:
        """Sauvegarde les produits dans le dossier data/ au format JSON."""
        chemin = Path(chemin_fichier)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        donnees = [p.to_dict() for p in self._produits]
        with open(chemin, mode="w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        return chemin

    def sauvegarder_sqlite(self, chemin_db: Path) -> Path:
        """
        Enregistre les produits dans une base de données SQLite (data/amazon_tech.db).
        """
        chemin = Path(chemin_db)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(chemin)
        try:
            curseur = conn.cursor()
            curseur.execute(
                """
                CREATE TABLE IF NOT EXISTS produits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT NOT NULL,
                    prix REAL NOT NULL,
                    categorie TEXT NOT NULL,
                    note REAL,
                    nb_avis INTEGER,
                    disponibilite TEXT,
                    image TEXT,
                    description TEXT,
                    url TEXT
                )
                """
            )
            curseur.execute("DELETE FROM produits")
            curseur.executemany(
                """
                INSERT INTO produits (
                    titre, prix, categorie, note, nb_avis,
                    disponibilite, image, description, url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        p.titre,
                        p.prix,
                        p.categorie,
                        p.note,
                        p.nb_avis,
                        p.disponibilite,
                        p.image,
                        p.description,
                        p.url,
                    )
                    for p in self._produits
                ],
            )
            conn.commit()
        finally:
            conn.close()
        return chemin
