"""Parsing et extraction des donnees avec selecteurs CSS"""
import re
from typing import Optional, Dict, Any
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


MARQUES_CONNUES = [
    "Apple", "iPhone", "Samsung", "Sony", "JBL", "Bose", "Xiaomi", "Huawei",
    "Google", "Pixel", "OnePlus", "Lenovo", "Dell", "HP", "Asus", "Acer",
    "Sennheiser", "Anker", "Soundcore", "Logitech", "Marshall", "Beats", "Jabra"
]


class AmazonParser:
    @staticmethod
    def extraire_titre(element: WebElement) -> str:
        selecteurs = [
            "h2 span",
            "h2 a span",
            "h2 a",
            "span.a-size-medium.a-color-base.a-text-normal",
            "span.a-size-base-plus.a-color-base.a-text-normal"
        ]
        for sel in selecteurs:
            matches = element.find_elements(By.CSS_SELECTOR, sel)
            for el in matches:
                txt = el.text.strip()
                if txt:
                    return txt
        return "Titre non disponible"

    @staticmethod
    def extraire_prix(element: WebElement) -> Optional[float]:
        selecteurs = [
            "span.a-price span.a-offscreen",
            "span.a-price-whole",
            "span.a-color-base"
        ]
        for sel in selecteurs:
            matches = element.find_elements(By.CSS_SELECTOR, sel)
            for el in matches:
                txt = el.get_attribute("textContent") or el.text
                prix = AmazonParser.nettoyer_prix(txt)
                if prix is not None:
                    return prix
        return None

    @staticmethod
    def nettoyer_prix(texte_prix: str) -> Optional[float]:
        if not texte_prix:
            return None
        nettoye = texte_prix.replace("\xa0", " ").replace("€", "").replace("$", "").replace("£", "").strip()
        match = re.search(r"(\d+[\s\d]*)[,\.](\d{2})", nettoye)
        if match:
            entier = match.group(1).replace(" ", "")
            decimal = match.group(2)
            try:
                return float(f"{entier}.{decimal}")
            except ValueError:
                pass
        match_entier = re.search(r"(\d+[\s\d]*)", nettoye)
        if match_entier:
            entier = match_entier.group(1).replace(" ", "")
            try:
                return float(entier)
            except ValueError:
                pass
        return None

    @staticmethod
    def extraire_note(element: WebElement) -> Optional[str]:
        selecteurs = [
            "i.a-icon-star-small span.a-icon-alt",
            "span.a-icon-alt",
            "i.a-icon-star span.a-icon-alt"
        ]
        for sel in selecteurs:
            matches = element.find_elements(By.CSS_SELECTOR, sel)
            for el in matches:
                txt = el.get_attribute("textContent") or el.text
                if txt and ("étoile" in txt.lower() or "star" in txt.lower()):
                    return txt.strip()
        return None

    @staticmethod
    def extraire_image(element: WebElement) -> Optional[str]:
        imgs = element.find_elements(By.CSS_SELECTOR, "img.s-image, img.s-access-image")
        if imgs:
            img = imgs[0]
            # Verifier les attributs possibles d'images reelles (en evitant les placeholders 1x1)
            for attr in ["src", "data-src", "data-lazy-src", "srcset"]:
                val = img.get_attribute(attr)
                if val and val.startswith("http") and "grey-pixel" not in val and "data:image" not in val:
                    if attr == "srcset":
                        val = val.split()[0].strip()
                    return val
        return None

    @staticmethod
    def extraire_url_produit(element: WebElement) -> Optional[str]:
        selecteurs = [
            "h2 a.a-link-normal",
            "a.a-link-normal.s-no-outline",
            "a.a-link-normal.s-underline-text"
        ]
        for sel in selecteurs:
            links = element.find_elements(By.CSS_SELECTOR, sel)
            if links:
                url = links[0].get_attribute("href")
                if url:
                    return url
        return None

    @staticmethod
    def detecter_marque(titre: str) -> str:
        titre_lower = titre.lower()
        for marque in MARQUES_CONNUES:
            if re.search(r"\b" + re.escape(marque.lower()) + r"\b", titre_lower):
                return marque
        mots = titre.split()
        if mots:
            premier = mots[0].capitalize()
            if len(premier) >= 2:
                return premier
        return "Générique"

    @classmethod
    def parser_element(cls, element: WebElement, categorie: str) -> Dict[str, Any]:
        titre = cls.extraire_titre(element)
        prix = cls.extraire_prix(element)
        note = cls.extraire_note(element)
        url_image = cls.extraire_image(element)
        url_produit = cls.extraire_url_produit(element)
        marque = cls.detecter_marque(titre)

        return {
            "titre": titre,
            "prix": prix,
            "note": note,
            "disponibilite": "En stock",
            "url_image": url_image,
            "image_path": None,
            "categorie": categorie,
            "marque": marque,
            "url_produit": url_produit,
        }
