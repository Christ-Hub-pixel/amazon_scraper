"""Gestion des exports CSV"""
import csv
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import config
from app.models.produit import Produit


class ExportView:
    @staticmethod
    def exporter_categorie_csv(produits: List[Produit], categorie: str) -> Path:
        nom_dossier = categorie.lower().replace(" ", "_")
        dossier_cat = config.TECH_DATA_DIR / nom_dossier
        dossier_cat.mkdir(parents=True, exist_ok=True)
        chemin_csv = dossier_cat / "data.csv"

        champs = [
            "titre", "prix", "note", "disponibilite",
            "marque", "categorie", "image_path", "url_image", "url_produit"
        ]

        with open(chemin_csv, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=champs)
            writer.writeheader()
            for p in produits:
                writer.writerow(p.to_dict())

        return chemin_csv

    @staticmethod
    def mettre_a_jour_recap(stats_categorie: Dict[str, Any]) -> Path:
        chemin_recap = config.RECAP_CSV_PATH
        existe = chemin_recap.exists()

        champs = ["categorie", "nb_produits", "prix_moyen", "prix_max", "date_scraping"]

        with open(chemin_recap, mode="a" if existe else "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=champs)
            if not existe:
                writer.writeheader()
            writer.writerow({
                "categorie": stats_categorie.get("categorie", "Inconnue"),
                "nb_produits": stats_categorie.get("nb_produits", 0),
                "prix_moyen": stats_categorie.get("prix_moyen", 0.0),
                "prix_max": stats_categorie.get("prix_max", 0.0),
                "date_scraping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return chemin_recap

    @staticmethod
    def exporter_general_csv(produits: List[Produit], nom_fichier: str = "export_produits.csv") -> Path:
        chemin_export = config.EXPORT_DIR / nom_fichier
        champs = [
            "titre", "prix", "note", "disponibilite",
            "marque", "categorie", "image_path", "url_image", "url_produit"
        ]

        with open(chemin_export, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=champs)
            writer.writeheader()
            for p in produits:
                writer.writerow(p.to_dict())

        return chemin_export
