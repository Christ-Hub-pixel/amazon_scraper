"""Gestion de la base de donnees SQLite"""
import sqlite3
from typing import List, Dict, Any
from pathlib import Path
from contextlib import closing
from config import DB_PATH
from app.models.produit import Produit


class Depot:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._initialiser_base()

    def _initialiser_base(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT NOT NULL,
                    prix REAL,
                    note TEXT,
                    disponibilite TEXT,
                    url_image TEXT,
                    image_path TEXT,
                    categorie TEXT,
                    marque TEXT,
                    url_produit TEXT,
                    date_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def sauvegarder_produit(self, produit: Produit) -> int:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM produits WHERE titre = ? AND categorie = ?",
                (produit.titre, produit.categorie)
            )
            existant = cursor.fetchone()
            if existant:
                cursor.execute("""
                    UPDATE produits SET
                        prix = ?, note = ?, disponibilite = ?,
                        url_image = ?, image_path = COALESCE(?, image_path),
                        marque = ?, url_produit = ?, date_scraping = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    produit.prix, produit.note, produit.disponibilite,
                    produit.url_image, produit.image_path,
                    produit.marque, produit.url_produit, existant[0]
                ))
                conn.commit()
                return existant[0]
            else:
                cursor.execute("""
                    INSERT INTO produits (
                        titre, prix, note, disponibilite,
                        url_image, image_path, categorie, marque, url_produit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    produit.titre, produit.prix, produit.note, produit.disponibilite,
                    produit.url_image, produit.image_path, produit.categorie, produit.marque, produit.url_produit
                ))
                conn.commit()
                return cursor.lastrowid

    def sauvegarder_produits(self, produits: List[Produit]) -> int:
        nb_ajouts = 0
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            for p in produits:
                cursor.execute(
                    "SELECT id FROM produits WHERE titre = ? AND categorie = ?",
                    (p.titre, p.categorie)
                )
                existant = cursor.fetchone()
                if existant:
                    cursor.execute("""
                        UPDATE produits SET
                            prix = ?, note = ?, disponibilite = ?,
                            url_image = ?, image_path = COALESCE(?, image_path),
                            marque = ?, url_produit = ?, date_scraping = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        p.prix, p.note, p.disponibilite,
                        p.url_image, p.image_path,
                        p.marque, p.url_produit, existant[0]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO produits (
                            titre, prix, note, disponibilite,
                            url_image, image_path, categorie, marque, url_produit
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        p.titre, p.prix, p.note, p.disponibilite,
                        p.url_image, p.image_path, p.categorie, p.marque, p.url_produit
                    ))
                nb_ajouts += 1
            conn.commit()
        return nb_ajouts

    def obtenir_tous(self) -> List[Produit]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produits ORDER BY id DESC")
            lignes = cursor.fetchall()
            return [
                Produit(
                    titre=l["titre"],
                    prix=l["prix"],
                    note=l["note"],
                    disponibilite=l["disponibilite"],
                    url_image=l["url_image"],
                    image_path=l["image_path"],
                    categorie=l["categorie"],
                    marque=l["marque"],
                    url_produit=l["url_produit"]
                )
                for l in lignes
            ]

    def filtrer_par_marque(self, marque: str) -> List[Produit]:
        terme = f"%{marque.lower()}%"
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM produits 
                WHERE LOWER(marque) LIKE ? OR LOWER(titre) LIKE ?
                ORDER BY prix ASC
            """, (terme, terme))
            lignes = cursor.fetchall()
            return [
                Produit(
                    titre=l["titre"],
                    prix=l["prix"],
                    note=l["note"],
                    disponibilite=l["disponibilite"],
                    url_image=l["url_image"],
                    image_path=l["image_path"],
                    categorie=l["categorie"],
                    marque=l["marque"],
                    url_produit=l["url_produit"]
                )
                for l in lignes
            ]

    def calculer_statistiques(self) -> Dict[str, Any]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(prix) as nb_avec_prix,
                    AVG(prix) as prix_moyen,
                    MAX(prix) as prix_max,
                    MIN(prix) as prix_min
                FROM produits
                WHERE prix IS NOT NULL AND prix > 0
            """)
            stats_prix = cursor.fetchone()

            cursor.execute("""
                SELECT categorie, COUNT(*) as total
                FROM produits
                GROUP BY categorie
            """)
            par_categorie = {row["categorie"]: row["total"] for row in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) as total_general FROM produits")
            total_general = cursor.fetchone()["total_general"]

            return {
                "total_produits": total_general,
                "nb_avec_prix": stats_prix["nb_avec_prix"] if stats_prix else 0,
                "prix_moyen": round(stats_prix["prix_moyen"], 2) if (stats_prix and stats_prix["prix_moyen"]) else 0.0,
                "prix_max": round(stats_prix["prix_max"], 2) if (stats_prix and stats_prix["prix_max"]) else 0.0,
                "prix_min": round(stats_prix["prix_min"], 2) if (stats_prix and stats_prix["prix_min"]) else 0.0,
                "par_categorie": par_categorie
            }
