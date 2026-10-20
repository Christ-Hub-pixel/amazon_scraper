"""
Modèle POO représentant un produit technologique extrait lors du scraping.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Produit:
    """
    Représente un produit Amazon (nom/titre, prix, image, description,
    catégorie, note, nombre d'avis, disponibilité, url).
    """

    titre: str
    prix: float
    categorie: str
    image: str = ""
    description: str = ""
    note: Optional[float] = None
    nb_avis: int = 0
    disponibilite: str = "En stock"
    url: str = ""

    def __post_init__(self) -> None:
        self.titre = self.titre.strip()
        self.categorie = self.categorie.strip()
        self.prix = round(float(self.prix), 2)
        if not self.description:
            self.description = f"Produit technologique ({self.categorie}) : {self.titre}"
        if self.note is not None:
            self.note = round(float(self.note), 1)
        self.nb_avis = int(self.nb_avis)

    @property
    def nom(self) -> str:
        """Alias pour le titre du produit."""
        return self.titre

    def correspond_marque(self, marque: str) -> bool:
        """Vérifie si le titre du produit correspond à la marque recherchée (ex: 'iphone')."""
        terme = marque.strip().lower()
        return terme in self.titre.lower()

    def to_dict(self) -> dict:
        """Convertit l'objet Produit en dictionnaire (pour export CSV / JSON / SQLite)."""
        return {
            "titre": self.titre,
            "prix": self.prix,
            "categorie": self.categorie,
            "note": self.note if self.note is not None else "",
            "nb_avis": self.nb_avis,
            "disponibilite": self.disponibilite,
            "image": self.image,
            "description": self.description,
            "url": self.url,
        }

    def __str__(self) -> str:
        note_str = f"{self.note}/5" if self.note is not None else "N/A"
        return f"[{self.categorie}] {self.titre[:52]}... | {self.prix:.2f} € | Note: {note_str}"
