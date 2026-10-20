"""
Gestionnaire du navigateur Selenium (WebDriver) pour les pages dynamiques.
Conforme à la Séance 2 : utilisation de ChromeOptions (--headless=new) ou Firefox,
avec vérification des pilotes système et gestion stricte des timeouts pour éviter tout blocage.
"""

import shutil
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Optional

try:
    from selenium import webdriver
except ImportError:
    webdriver = None  # type: ignore

import config


class DriverManager:
    """Classe POO responsable de l'initialisation et de la fermeture du WebDriver Selenium."""

    def __init__(self, headless: bool = config.HEADLESS) -> None:
        self.headless = headless
        self.pilote: Optional[Any] = None
        self._initialisation_echouee: bool = False

    def creer_pilote(self) -> Optional[Any]:
        """
        Crée et configure une instance du pilote Selenium (Chrome ou Firefox)
        avec un timeout strict pour ne jamais bloquer le terminal si aucun
        navigateur/driver (chromedriver / geckodriver) n'est installé sur la machine.
        """
        if webdriver is None or self._initialisation_echouee:
            return None

        # Vérifier la présence d'un driver ou navigateur compatible avant de lancer Selenium
        a_chrome = bool(
            shutil.which("chromedriver")
            and (
                shutil.which("google-chrome")
                or shutil.which("chromium")
                or shutil.which("chromium-browser")
            )
        )
        a_firefox = bool(shutil.which("geckodriver") and shutil.which("firefox"))

        if not a_chrome and not a_firefox:
            self._initialisation_echouee = True
            return None

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                futur = executor.submit(self._initialiser_webdriver, a_chrome, a_firefox)
                self.pilote = futur.result(timeout=5.0)
                return self.pilote
        except (FuturesTimeoutError, Exception):
            self._initialisation_echouee = True
            self.pilote = None
            return None

    def _initialiser_webdriver(
        self, a_chrome: bool, a_firefox: bool
    ) -> Optional[Any]:
        """Initialise concrètement Chrome ou Firefox avec les options headless et timeout."""
        if a_chrome:
            try:
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless=new")
                options.add_argument(f"user-agent={config.USER_AGENT}")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--lang=fr-FR")

                pilote = webdriver.Chrome(options=options)
                pilote.set_page_load_timeout(config.TIMEOUT)
                return pilote
            except Exception:
                pass

        if a_firefox:
            try:
                options_ff = webdriver.FirefoxOptions()
                if self.headless:
                    options_ff.add_argument("--headless")
                options_ff.set_preference(
                    "general.useragent.override", config.USER_AGENT
                )
                options_ff.set_preference("intl.accept_languages", "fr-FR, fr")

                pilote = webdriver.Firefox(options=options_ff)
                pilote.set_page_load_timeout(config.TIMEOUT)
                return pilote
            except Exception:
                pass

        return None

    def fermer_pilote(self) -> None:
        """Ferme proprement le navigateur Selenium."""
        if self.pilote is not None:
            try:
                self.pilote.quit()
            except Exception:
                pass
            finally:
                self.pilote = None
