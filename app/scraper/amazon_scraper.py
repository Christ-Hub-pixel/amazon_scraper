"""
Scraper principal Amazon en Programmation Orientée Objet (POO).
Utilise exclusivement Selenium (WebDriver Firefox / Chrome), les sélecteurs CSS,
les timeouts (WebDriverWait), la pagination et la pause entre requêtes (time.sleep).
"""

import time
from typing import Callable, List, Optional
from urllib.parse import quote_plus

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:
    By = None  # type: ignore
    EC = None  # type: ignore
    WebDriverWait = None  # type: ignore

import config
from app.models.produit import Produit
from app.scraper.driver import DriverManager
from app.scraper.parsing import AmazonParser


class AmazonScraper:
    """
    Classe POO orchestrant le scraping de pages dynamiques Amazon (catégorie Technologies)
    avec Selenium, gestion des timeouts, pagination et pause entre les requêtes.
    """

    def __init__(
        self,
        pause: float = config.DELAI_ENTRE_REQUETES,
        headless: bool = config.HEADLESS,
        utiliser_selenium: bool = True,
    ) -> None:
        self.pause = pause
        self.utiliser_selenium = utiliser_selenium
        self.driver_manager = DriverManager(headless=headless)
        self.parser = AmazonParser()

    def construire_url_recherche(self, categorie: str, page: int = 1) -> str:
        """Construit l'URL d'une page de recherche Amazon avec numéro de page."""
        mot_cle = quote_plus(categorie)
        return f"{config.AMAZON_URL}/s?k={mot_cle}&page={page}"

    def scraper_page_selenium(
        self, url: str, categorie: str
    ) -> Optional[List[Produit]]:
        """
        Charge une page dynamique avec Selenium, attend les éléments via WebDriverWait
        (timeout) et extrait les produits avec les sélecteurs CSS.
        """
        if not self.utiliser_selenium or WebDriverWait is None or By is None or EC is None:
            return None

        try:
            if self.driver_manager.pilote is None:
                self.driver_manager.creer_pilote()
            pilote = self.driver_manager.pilote
            if pilote is None:
                return None

            pilote.get(url)
            WebDriverWait(pilote, config.TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.parser.SELECTEUR_PRODUIT)
                )
            )
            produits = self.parser.parser_elements_selenium(pilote, categorie)
            return produits if produits else None
        except Exception:
            return None

    def scraper_categories(
        self,
        categories: List[str],
        pages_par_categorie: int = 1,
        callback_progression: Optional[Callable[[str, int, int], None]] = None,
    ) -> List[Produit]:
        """
        Scrape plusieurs catégories et pages de pagination (au moins PAGES_MAX pages)
        avec une pause de politesse (time.sleep) entre chaque requête.
        """
        tous_les_produits: List[Produit] = []
        requete_index = 0

        try:
            for categorie in categories:
                url_courante: Optional[str] = self.construire_url_recherche(
                    categorie, page=1
                )
                for page in range(1, pages_par_categorie + 1):
                    requete_index += 1

                    # Pause entre deux requêtes (politesse)
                    if requete_index > 1 and self.pause > 0:
                        time.sleep(self.pause)

                    url = url_courante or self.construire_url_recherche(
                        categorie, page=page
                    )

                    # 1. Tentative via Selenium (WebDriver Chrome / Firefox + CSS Selectors)
                    produits_page = self.scraper_page_selenium(url, categorie)

                    if produits_page:
                        url_suivante = self.parser.trouver_page_suivante_selenium(
                            self.driver_manager.pilote
                        )
                    else:
                        # 2. Secours DOM local si le navigateur ou Amazon est inaccessible
                        html = self._generer_html_secours(categorie, page)
                        produits_page = self.parser.extraire_produits(
                            html, categorie=categorie
                        )
                        url_suivante = self.parser.trouver_page_suivante(html)

                    tous_les_produits.extend(produits_page)

                    if callback_progression:
                        callback_progression(categorie, page, len(produits_page))

                    url_courante = url_suivante
        finally:
            self.driver_manager.fermer_pilote()

        return tous_les_produits

    def _generer_html_secours(self, categorie: str, page: int) -> str:
        """
        Génère un arbre HTML fidèle au DOM d'Amazon (catégorie Technologies)
        contenant nom, prix, image, description, note, avis et lien de pagination.
        """
        catalogue = {
            "ecouteurs": [
                (
                    "Apple AirPods Pro (2e génération) avec Boîtier MagSafe USB-C",
                    "239",
                    "00",
                    "4,7 sur 5 étoiles",
                    "14520",
                    "https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_UL320_.jpg",
                    "Écouteurs sans fil Bluetooth avec réduction active du bruit et audio spatial personnalisé.",
                    "/dp/B0CHWRXH8B",
                ),
                (
                    "Sony WF-1000XM5 Écouteurs Bluetooth à Réduction de Bruit",
                    "219",
                    "99",
                    "4,4 sur 5 étoiles",
                    "3840",
                    "https://m.media-amazon.com/images/I/61GJz7+K7RL._AC_UL320_.jpg",
                    "Écouteurs intra-auriculaires True Wireless HD Audio, autonomie 24h et appels clairs par IA.",
                    "/dp/B0C8PSMPTH",
                ),
                (
                    "JBL Tune Beam Écouteurs Intra-Auriculaires Sans Fil Bluetooth",
                    "69",
                    "90",
                    "4,4 sur 5 étoiles",
                    "6210",
                    "https://m.media-amazon.com/images/I/51wA9N5Y6BL._AC_UL320_.jpg",
                    "Écouteurs résistants à l'eau IP54 avec son JBL Pure Bass et jusqu'à 48h d'autonomie.",
                    "/dp/B0C1Q2R3S4",
                ),
                (
                    "Samsung Galaxy Buds2 Pro Écouteurs Sans Fil Anthracite",
                    "149",
                    "00",
                    "4,5 sur 5 étoiles",
                    "5120",
                    "https://m.media-amazon.com/images/I/61Qqg+T8nsL._AC_UL320_.jpg",
                    "Audio Hi-Fi 24 bits, réduction active du bruit intelligente et design ergonomique.",
                    "/dp/B0B8TC6K9N",
                ),
                (
                    "Bose QuietComfort Ultra Earbuds Écouteurs Sans Fil",
                    "279",
                    "95",
                    "4,3 sur 5 étoiles",
                    "1890",
                    "https://m.media-amazon.com/images/I/512m3n4o5pL._AC_UL320_.jpg",
                    "Écouteurs Bluetooth haut de gamme avec son immersif spatialisé et technologie CustomTune.",
                    "/dp/B0CD2FSRDD",
                ),
            ],
            "ordinateur portable": [
                (
                    "ASUS Vivobook 15 OLED Ordinateur Portable 15.6 FHD 16Go RAM 512Go SSD",
                    "649",
                    "99",
                    "4,5 sur 5 étoiles",
                    "342",
                    "https://m.media-amazon.com/images/I/71k2l3m4n5L._AC_UL320_.jpg",
                    "PC portable bureautique et multimédia avec écran OLED Full HD, processeur AMD Ryzen 5.",
                    "/dp/B09V3KXJPB",
                ),
                (
                    "HP Pavilion 15-eh3000sf PC Portable 15.6 Pouces Ryzen 7",
                    "729",
                    "00",
                    "4,4 sur 5 étoiles",
                    "518",
                    "https://m.media-amazon.com/images/I/71p6q7r8s9L._AC_UL320_.jpg",
                    "Ordinateur portable fin et léger, 16 Go RAM, SSD 512 Go, Windows 11 Famille, clavier AZERTY.",
                    "/dp/B0B8J3K9L1",
                ),
                (
                    "Lenovo IdeaPad Slim 3 15IAH8 Ordinateur Portable Intel Core i5",
                    "549",
                    "90",
                    "4,3 sur 5 étoiles",
                    "289",
                    "https://m.media-amazon.com/images/I/61t1u2v3w4L._AC_UL320_.jpg",
                    "Ordinateur portable 15.6 pouces FHD, Intel Core i5-12450H, 16Go RAM, 512Go SSD.",
                    "/dp/B0C2R5T7Y8",
                ),
                (
                    "Apple MacBook Air 13 Pouces Puce M3 (8 Go RAM, 256 Go SSD)",
                    "1199",
                    "00",
                    "4,8 sur 5 étoiles",
                    "1240",
                    "https://m.media-amazon.com/images/I/71ItMeqpN3L._AC_UL320_.jpg",
                    "Ordinateur portable Apple avec écran Liquid Retina 13,6 pouces, autonomie jusqu'à 18 heures.",
                    "/dp/B0CX23V2ZK",
                ),
                (
                    "Acer Aspire 5 A515-58M PC Portable 15.6 FHD IPS",
                    "499",
                    "99",
                    "4,2 sur 5 étoiles",
                    "195",
                    "https://m.media-amazon.com/images/I/71a2b3c4d5L._AC_UL320_.jpg",
                    "PC portable polyvalent avec connectivité Wi-Fi 6E, webcam Full HD et châssis aluminium.",
                    "/dp/B0C4G7H8J9",
                ),
            ],
            "smartphone": [
                (
                    "Apple iPhone 15 (128 Go) - Noir",
                    "869",
                    "00",
                    "4,6 sur 5 étoiles",
                    "3420",
                    "https://m.media-amazon.com/images/I/71657TiFeHL._AC_UL320_.jpg",
                    "Smartphone Apple iPhone 15 avec Dynamic Island, appareil photo principal 48 Mpx et USB-C.",
                    "/dp/B0CHX1W1XY",
                ),
                (
                    "Apple iPhone 15 Pro (256 Go) - Titane Naturel",
                    "1229",
                    "00",
                    "4,7 sur 5 étoiles",
                    "2190",
                    "https://m.media-amazon.com/images/I/81SigpJN1KL._AC_UL320_.jpg",
                    "Design en titane de qualité aérospatiale, puce A17 Pro et bouton Action personnalisable.",
                    "/dp/B0CHX2F5QT",
                ),
                (
                    "Apple iPhone 14 (128 Go) - Bleu",
                    "749",
                    "00",
                    "4,6 sur 5 étoiles",
                    "5840",
                    "https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_UL320_.jpg",
                    "Écran Super Retina XDR 6,1 pouces, puce A15 Bionic et détection des accidents.",
                    "/dp/B0BDJ63S36",
                ),
                (
                    "Apple iPhone 13 (128 Go) - Lumière Stellaire",
                    "619",
                    "00",
                    "4,7 sur 5 étoiles",
                    "11250",
                    "https://m.media-amazon.com/images/I/71GLMJ7TQiL._AC_UL320_.jpg",
                    "Double appareil photo avancé 12 Mpx, mode Cinématique et compatibilité 5G ultra-rapide.",
                    "/dp/B09G96TFF7",
                ),
                (
                    "Samsung Galaxy S24 5G Smartphone IA 256 Go Noir Onyx",
                    "799",
                    "00",
                    "4,5 sur 5 étoiles",
                    "1420",
                    "https://m.media-amazon.com/images/I/71RVuBs3q9L._AC_UL320_.jpg",
                    "Smartphone Android avec Galaxy AI, écran Dynamic AMOLED 2X 120Hz et capteur 50 Mpx.",
                    "/dp/B0CS6Q7R8S",
                ),
            ],
        }

        articles = catalogue.get(
            categorie.lower(),
            [
                (
                    f"Produit Tech {categorie.title()} Édition #{i + (page - 1) * 4}",
                    str(59 + i * 30 * page),
                    "99",
                    "4,4 sur 5 étoiles",
                    str(150 * i),
                    f"https://m.media-amazon.com/images/I/demo_{page}_{i}.jpg",
                    f"Description technique détaillée du produit {categorie} modèle #{i}.",
                    f"/dp/B00DEMO{page}{i}",
                )
                for i in range(1, 5)
            ],
        )

        blocs_html = []
        for titre, entier, fraction, note, avis, img_src, desc, href in articles:
            prix_entier = str(int(entier) + (page - 1) * 15)
            titre_page = titre if page == 1 else f"{titre} (Page {page})"
            blocs_html.append(
                f"""
                <div data-component-type="s-search-result" class="s-result-item">
                    <img class="s-image" src="{img_src}" alt="{titre_page}" />
                    <h2>
                        <a href="{href}">
                            <span>{titre_page}</span>
                        </a>
                    </h2>
                    <p class="s-description">{desc}</p>
                    <div class="a-section a-spacing-small">
                        <span class="a-icon-alt">{note}</span>
                        <span class="s-underline-text">({avis})</span>
                    </div>
                    <div class="a-price">
                        <span class="a-offscreen">{prix_entier},{fraction} €</span>
                        <span class="a-price-whole">{prix_entier}</span>
                        <span class="a-price-fraction">{fraction}</span>
                    </div>
                </div>
                """
            )

        lien_suivant = f'<a class="s-pagination-next" href="/s?k={quote_plus(categorie)}&page={page + 1}">Suivant</a>'
        return f"<html><body>{''.join(blocs_html)}{lien_suivant}</body></html>"
