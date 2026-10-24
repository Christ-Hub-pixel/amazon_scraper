"""Modele Produit"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Produit:
    titre: str
    prix: Optional[float] = None
    note: Optional[str] = None
    disponibilite: Optional[str] = "En stock"
    url_image: Optional[str] = None
    image_path: Optional[str] = None
    categorie: Optional[str] = "technologies"
    marque: Optional[str] = "Inconnue"
    url_produit: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Produit":
        return cls(
            titre=data.get("titre", ""),
            prix=data.get("prix"),
            note=data.get("note"),
            disponibilite=data.get("disponibilite", "En stock"),
            url_image=data.get("url_image"),
            image_path=data.get("image_path"),
            categorie=data.get("categorie", "technologies"),
            marque=data.get("marque", "Inconnue"),
            url_produit=data.get("url_produit"),
        )
