"""
Vue d'exportation (ExportView) :
- Enregistre tous les produits dans exports/produits_amazon.csv
- Organise le dossier data/tech/<categorie>/data.csv et data/tech/<categorie>/images/
- Génère data/recap.csv à la racine de data/ avec le récapitulatif des catégories scrapées.
"""

import base64
import csv
import re
from pathlib import Path
from typing import List

import config
from app.models.depot import DepotProduits
from app.models.produit import Produit

# Miniature PNG 1x1 valide encodée en base64 (utilisée pour créer image_1.png hors-ligne)
PNG_MINIATURE_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


class ExportView:
    """Classe POO responsable de l'exportation des données en fichiers CSV et dossiers images."""

    CHAMPS_CSV = [
        "titre",
        "prix",
        "categorie",
        "note",
        "nb_avis",
        "disponibilite",
        "image",
        "description",
        "url",
    ]

    def exporter_csv(self, produits: List[Produit], chemin_fichier: Path) -> Path:
        """
        Enregistre une liste d'objets Produit dans un fichier CSV encodé en UTF-8.
        """
        chemin = Path(chemin_fichier)
        chemin.parent.mkdir(parents=True, exist_ok=True)

        with open(chemin, mode="w", newline="", encoding="utf-8") as fichier_csv:
            writer = csv.DictWriter(fichier_csv, fieldnames=self.CHAMPS_CSV)
            writer.writeheader()
            for produit in produits:
                writer.writerow(produit.to_dict())

        return chemin

    def exporter_arborescence_data(self, depot: DepotProduits) -> Path:
        """
        Crée l'arborescence demandée dans le cahier des charges :
        - data/tech/<categorie>/data.csv
        - data/tech/<categorie>/images/image 1.png (et liens_images.csv)
        - data/recap.csv (résumé du nombre de catégories scrapées et statistiques)
        """
        stats = depot.obtenir_statistiques()
        details_categories = stats.get("details_categories", {})

        for categorie, infos in details_categories.items():
            nom_dossier = re.sub(r"[^\w\-]+", "_", categorie.strip().lower())
            dossier_cat = config.TECH_DIR / nom_dossier
            dossier_images = dossier_cat / "images"
            dossier_images.mkdir(parents=True, exist_ok=True)

            produits_cat = depot.filtrer_par_categorie(categorie)
            self.exporter_csv(produits_cat, dossier_cat / "data.csv")

            # Enregistrement des images (miniatures PNG + index des URLs d'images)
            chemin_index_images = dossier_images / "liens_images.csv"
            with open(
                chemin_index_images, mode="w", newline="", encoding="utf-8"
            ) as f_img:
                writer = csv.writer(f_img)
                writer.writerow(["fichier_local", "titre_produit", "url_image"])
                for idx, prod in enumerate(produits_cat, start=1):
                    nom_img = f"image {idx}.png"
                    chemin_png = dossier_images / nom_img
                    if not chemin_png.exists():
                        chemin_png.write_bytes(PNG_MINIATURE_BYTES)
                    writer.writerow([nom_img, prod.titre, prod.image])

        # Génération de data/recap.csv
        chemin_recap = config.FICHIER_RECAP_CSV
        chemin_recap.parent.mkdir(parents=True, exist_ok=True)
        with open(chemin_recap, mode="w", newline="", encoding="utf-8") as f_recap:
            writer = csv.writer(f_recap)
            writer.writerow(
                [
                    "nb_total_categories_scrapees",
                    "categorie",
                    "nombre_produits",
                    "prix_moyen",
                    "prix_max",
                    "prix_min",
                ]
            )
            nb_cats = len(details_categories)
            for categorie, infos in details_categories.items():
                writer.writerow(
                    [
                        nb_cats,
                        categorie,
                        infos["nb_produits"],
                        infos["prix_moyen"],
                        infos["prix_max"],
                        infos["prix_min"],
                    ]
                )

        return chemin_recap
