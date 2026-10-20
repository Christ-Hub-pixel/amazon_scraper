"""
Module de parsing utilisant les sélecteurs CSS avec Selenium (By.CSS_SELECTOR)
pour extraire : le nom, le prix, l'image, la description, la note et la pagination.
Aucune donnée à caractère personnel n'est collectée.
"""

import re
from typing import Any, List, Optional

try:
    from selenium.webdriver.common.by import By
except ImportError:
    By = None  # type: ignore

import config
from app.models.produit import Produit


class AmazonParser:
    """Classe POO dédiée à l'extraction des produits via les sélecteurs CSS."""

    # Sélecteurs CSS pour Amazon (Catégorie Technologies)
    SELECTEUR_PRODUIT = 'div[data-component-type="s-search-result"]'
    SELECTEUR_NOM = "h2 a span, h2 span"
    SELECTEUR_LIEN = "h2 a"
    SELECTEUR_IMAGE = "img.s-image"
    SELECTEUR_DESCRIPTION = "p.s-description, div.s-title-instructions-style"
    SELECTEUR_PRIX_ENTIER = "span.a-price-whole"
    SELECTEUR_PRIX_FRACTION = "span.a-price-fraction"
    SELECTEUR_NOTE = "span.a-icon-alt"
    SELECTEUR_NB_AVIS = "span.s-underline-text"
    SELECTEUR_PAGE_SUIVANTE = "a.s-pagination-next"

    def parser_elements_selenium(
        self, pilote: Any, categorie: str
    ) -> List[Produit]:
        """
        Extrait la liste des produits directement depuis le pilote Selenium
        en utilisant les sélecteurs CSS (By.CSS_SELECTOR).
        """
        if pilote is None or By is None:
            return []

        produits: List[Produit] = []
        cartes = pilote.find_elements(By.CSS_SELECTOR, self.SELECTEUR_PRODUIT)

        for carte in cartes:
            produit = self._extraire_depuis_webelement(carte, categorie)
            if produit is not None:
                produits.append(produit)

        return produits

    def _extraire_depuis_webelement(
        self, carte: Any, categorie: str
    ) -> Optional[Produit]:
        """Extrait un objet Produit depuis un WebElement Selenium via By.CSS_SELECTOR."""
        try:
            # 1. Nom / Titre du produit
            elems_nom = carte.find_elements(By.CSS_SELECTOR, self.SELECTEUR_NOM)
            if not elems_nom:
                return None
            nom = elems_nom[0].text.strip()
            if not nom:
                return None

            # 2. Prix du produit
            elems_entier = carte.find_elements(
                By.CSS_SELECTOR, self.SELECTEUR_PRIX_ENTIER
            )
            if not elems_entier:
                return None
            entier = re.sub(r"[^\d]", "", elems_entier[0].text)
            if not entier:
                return None

            elems_fraction = carte.find_elements(
                By.CSS_SELECTOR, self.SELECTEUR_PRIX_FRACTION
            )
            fraction = (
                re.sub(r"[^\d]", "", elems_fraction[0].text)
                if elems_fraction
                else "00"
            )
            prix = float(f"{entier}.{fraction or '00'}")

            # 3. Lien de l'image du produit
            elems_img = carte.find_elements(By.CSS_SELECTOR, self.SELECTEUR_IMAGE)
            image_url = (
                elems_img[0].get_attribute("src") or "" if elems_img else ""
            )

            # 4. Description du produit
            elems_desc = carte.find_elements(
                By.CSS_SELECTOR, self.SELECTEUR_DESCRIPTION
            )
            description = (
                elems_desc[0].text.strip()
                if elems_desc and elems_desc[0].text.strip()
                else f"Produit technologique ({categorie}) : {nom}"
            )

            # 5. Note et avis
            note = None
            elems_note = carte.find_elements(By.CSS_SELECTOR, self.SELECTEUR_NOTE)
            if elems_note:
                texte_note = (
                    elems_note[0].get_attribute("innerHTML") or elems_note[0].text
                )
                match_note = re.search(
                    r"(\d+(?:\.\d+)?)", texte_note.replace(",", ".")
                )
                if match_note:
                    note = float(match_note.group(1))

            nb_avis = 0
            elems_avis = carte.find_elements(By.CSS_SELECTOR, self.SELECTEUR_NB_AVIS)
            if elems_avis:
                chiffres = re.sub(r"[^\d]", "", elems_avis[0].text)
                nb_avis = int(chiffres) if chiffres else 0

            # 6. URL de la fiche produit
            elems_lien = carte.find_elements(By.CSS_SELECTOR, self.SELECTEUR_LIEN)
            url = ""
            if elems_lien:
                href = elems_lien[0].get_attribute("href") or ""
                url = (
                    href
                    if href.startswith("http")
                    else (f"{config.AMAZON_URL}{href}" if href else "")
                )

            return Produit(
                titre=nom,
                prix=prix,
                categorie=categorie,
                image=image_url,
                description=description,
                note=note,
                nb_avis=nb_avis,
                disponibilite="En stock",
                url=url,
            )
        except Exception:
            return None

    def trouver_page_suivante_selenium(self, pilote: Any) -> Optional[str]:
        """Trouve le lien de la page suivante (pagination) via Selenium By.CSS_SELECTOR."""
        if pilote is None or By is None:
            return None
        try:
            liens = pilote.find_elements(
                By.CSS_SELECTOR, self.SELECTEUR_PAGE_SUIVANTE
            )
            if liens:
                href = liens[0].get_attribute("href")
                if href:
                    return (
                        href
                        if href.startswith("http")
                        else f"{config.AMAZON_URL}{href}"
                    )
        except Exception:
            pass
        return None

    def extraire_produits(self, html: str, categorie: str) -> List[Produit]:
        """
        Analyse une chaîne HTML (utilisée en mode de secours si Amazon bloque par CAPTCHA
        ou si aucun navigateur WebDriver n'est disponible).
        """
        produits: List[Produit] = []
        blocs = re.findall(
            r'<div[^>]*data-component-type="s-search-result"[^>]*>(.*?)</div>\s*</div>',
            html,
            flags=re.DOTALL,
        )
        for bloc in blocs:
            m_titre = re.search(r"<h2>.*?<span>(.*?)</span>.*?</h2>", bloc, re.DOTALL)
            m_lien = re.search(r'<h2>\s*<a[^>]*href="([^"]+)"', bloc, re.DOTALL)
            m_img = re.search(
                r'<img[^>]*class="[^"]*s-image[^"]*"[^>]*src="([^"]+)"', bloc
            )
            m_desc = re.search(
                r'<p[^>]*class="[^"]*s-description[^"]*"[^>]*>(.*?)</p>',
                bloc,
                re.DOTALL,
            )
            m_entier = re.search(r'<span class="a-price-whole">(.*?)</span>', bloc)
            m_frac = re.search(r'<span class="a-price-fraction">(.*?)</span>', bloc)
            m_note = re.search(r'<span class="a-icon-alt">(.*?)</span>', bloc)
            m_avis = re.search(r'<span class="s-underline-text">(.*?)</span>', bloc)

            if not m_titre or not m_entier:
                continue

            titre = m_titre.group(1).strip()
            entier = re.sub(r"[^\d]", "", m_entier.group(1))
            fraction = re.sub(r"[^\d]", "", m_frac.group(1)) if m_frac else "00"
            prix = float(f"{entier}.{fraction or '00'}")
            image_url = m_img.group(1).strip() if m_img else ""
            description = (
                m_desc.group(1).strip()
                if m_desc
                else f"Produit technologique ({categorie}) : {titre}"
            )
            note = None
            if m_note:
                mn = re.search(
                    r"(\d+(?:\.\d+)?)", m_note.group(1).replace(",", ".")
                )
                if mn:
                    note = float(mn.group(1))
            nb_avis = (
                int(re.sub(r"[^\d]", "", m_avis.group(1)) or "0") if m_avis else 0
            )
            href = m_lien.group(1).strip() if m_lien else ""
            url = (
                href
                if href.startswith("http")
                else (f"{config.AMAZON_URL}{href}" if href else "")
            )

            produits.append(
                Produit(
                    titre=titre,
                    prix=prix,
                    categorie=categorie,
                    image=image_url,
                    description=description,
                    note=note,
                    nb_avis=nb_avis,
                    disponibilite="En stock",
                    url=url,
                )
            )
        return produits

    def trouver_page_suivante(self, html: str) -> Optional[str]:
        """Récupère l'URL de la page suivante (pagination) depuis une chaîne HTML."""
        match = re.search(
            r'<a[^>]*class="[^"]*s-pagination-next[^"]*"[^>]*href="([^"]+)"', html
        )
        if match:
            href = match.group(1)
            return href if href.startswith("http") else f"{config.AMAZON_URL}{href}"
        return None
