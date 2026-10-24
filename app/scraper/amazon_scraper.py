"""Scraper Amazon utilisant Selenium"""
import time
import requests
from typing import List, Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config
from app.models.produit import Produit
from app.scraper.parsing import AmazonParser
from app.scraper.driver import creer_driver


class AmazonScraper:
    def __init__(self, driver: Optional[webdriver.Chrome] = None, headless: bool = config.HEADLESS):
        self.driver = driver or creer_driver(headless=headless)
        self.parser = AmazonParser()
        self._session_initialisee = False

    def initialiser_session(self) -> None:
        """Charge la page d'accueil Amazon et valide les cookies pour etablir une session valide"""
        if self._session_initialisee:
            return
        try:
            self.driver.get("https://www.amazon.fr")
            time.sleep(1.5)
            self.fermer_cookies()
            self._session_initialisee = True
        except Exception:
            pass

    def fermer_cookies(self) -> None:
        """Gere la banniere de cookies si elle est presente"""
        selecteurs = [
            "input#sp-cc-accept",
            "button#sp-cc-accept",
            "input[name='acceptCookie']",
            "#sp-cc-accept"
        ]
        for sel in selecteurs:
            try:
                bouton = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                bouton.click()
                time.sleep(0.5)
                break
            except Exception:
                continue

    def telecharger_image(self, url_image: str, dossier_cible: Path, nom_fichier: str) -> Optional[str]:
        """Telecharge l'image et retourne son chemin"""
        if not url_image or not url_image.startswith("http"):
            return None
        try:
            dossier_cible.mkdir(parents=True, exist_ok=True)
            extension = url_image.split(".")[-1].split("?")[0]
            if len(extension) > 4 or "/" in extension:
                extension = "jpg"
            chemin = dossier_cible / f"{nom_fichier}.{extension}"

            headers = {
                "User-Agent": config.USER_AGENT,
                "Referer": "https://www.amazon.fr/"
            }
            res = requests.get(url_image, headers=headers, timeout=8)
            if res.status_code == 200:
                with open(chemin, "wb") as f:
                    f.write(res.content)
                return str(chemin)
        except Exception:
            pass
        return None

    def scraper_categorie(self, mot_cle: str, nb_pages: int = config.PAGES_MAX, telecharger_images: bool = True) -> List[Produit]:
        """Scrape les produits d'une categorie sur nb_pages"""
        produits: List[Produit] = []
        dossier_images = config.TECH_DATA_DIR / mot_cle.lower().replace(" ", "_") / "images"

        # Initialiser la session au prealable pour eviter le blocage "Toutes nos excuses"
        self.initialiser_session()

        for page in range(1, nb_pages + 1):
            url_page = f"{config.AMAZON_URL}{mot_cle}" if page == 1 else f"{config.AMAZON_URL}{mot_cle}&page={page}"
            print(f"Scraping page {page}/{nb_pages} : {url_page}")
            self.driver.get(url_page)

            if page == 1:
                self.fermer_cookies()

            time.sleep(config.DELAI_ENTRE_REQUETES)

            # Verification si Amazon renvoie la page d'erreur 503 / robot
            tentatives = 0
            while "toutes nos excuses" in self.driver.title.lower() and tentatives < 2:
                tentatives += 1
                print(f"Page 'Toutes nos excuses' detectee. Re-tentative ({tentatives}/2)...", flush=True)
                time.sleep(2)
                self.driver.get("https://www.amazon.fr")
                time.sleep(1.5)
                self.driver.get(url_page)
                time.sleep(2)

            # Verification captcha
            if "captcha" in self.driver.current_url.lower() or "robot" in self.driver.title.lower():
                print("Captcha detecte. Veuillez le valider dans le navigateur...", flush=True)
                try:
                    WebDriverWait(self.driver, 20).until_not(
                        EC.title_contains("Robot Check")
                    )
                except Exception:
                    pass

            # Attendre l'affichage des resultats
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result'], div.s-result-item[data-asin]"))
                )
            except Exception:
                pass

            # Defilement fluide pour charger les images en differe (lazy loading)
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
                time.sleep(0.3)
                self.driver.execute_script("window.scrollTo(0, (document.body.scrollHeight / 3) * 2);")
                time.sleep(0.3)
                self.driver.execute_script("window.scrollTo(0, 0);")
            except Exception:
                pass

            cartes = self.driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            if not cartes:
                cartes = [
                    el for el in self.driver.find_elements(By.CSS_SELECTOR, "div.s-result-item[data-asin]")
                    if el.get_attribute("data-asin")
                ]

            print(f"-> {len(cartes)} produits detectes", flush=True)

            for carte in cartes:
                try:
                    data = self.parser.parser_element(carte, categorie=mot_cle)
                    if not data["titre"] or data["titre"] == "Titre non disponible":
                        continue

                    index_produit = len(produits) + 1
                    chemin_img = None
                    if telecharger_images and data["url_image"]:
                        chemin_img = self.telecharger_image(
                            url_image=data["url_image"],
                            dossier_cible=dossier_images,
                            nom_fichier=f"image_{index_produit}"
                        )
                    data["image_path"] = chemin_img

                    p = Produit.from_dict(data)
                    produits.append(p)
                    print(f"  [{index_produit}] {p.titre[:40]} | {p.prix} € | {p.marque}", flush=True)
                except Exception:
                    continue

            if page < nb_pages:
                time.sleep(config.DELAI_ENTRE_REQUETES)

        return produits

    def fermer(self) -> None:
        try:
            self.driver.quit()
        except Exception:
            pass
