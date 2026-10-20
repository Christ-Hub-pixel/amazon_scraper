"""
Module des compétences (Skills) de J.A.R.V.I.S. :
- Diagnostic système complet (CPU, RAM, Batterie, Disque)
- Pilotage vocal/texte du Scraper Amazon (scraping, filtre par marque, 3 statistiques)
- Recherche Web, ouverture de GitHub / YouTube / Google
- Notifications bureau Linux (notify-send)
- Heure, date et commandes d'assistance
"""

import datetime
import platform
import shutil
import subprocess
from urllib.parse import quote_plus

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

import config
from app.controllers.scraping_controller import ScrapingController


class CompetencesJarvis:
    """Regroupe toutes les actions et compétences exécutables par Jarvis."""

    def __init__(self) -> None:
        self.controleur_scraping = ScrapingController(
            pause=0.2, utiliser_selenium=True
        )

    def obtenir_salutation(self) -> str:
        """Retourne une salutation adaptée à l'heure de la journée."""
        heure = datetime.datetime.now().hour
        moment = "Bonjour" if 5 <= heure < 18 else "Bonsoir"
        return (
            f"{moment} Monsieur. Ici J.A.R.V.I.S., votre assistant personnel. "
            "Tous les systèmes sont opérationnels. Que puis-je faire pour vous ?"
        )

    def donner_heure_et_date(self) -> str:
        """Retourne la date et l'heure actuelles."""
        maintenant = datetime.datetime.now()
        return (
            f"Nous sommes le {maintenant.strftime('%d/%m/%Y')} "
            f"et il est exactement {maintenant.strftime('%H:%M:%S')}."
        )

    def diagnostic_systeme(self) -> str:
        """Analyse l'état du système Linux (CPU, mémoire vive, disque, batterie)."""
        os_info = f"{platform.system()} {platform.release()}"
        if psutil is None:
            return f"Système d'exploitation : {os_info}. Tous les modules principaux fonctionnent."

        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        disque = psutil.disk_usage("/")
        batterie = psutil.sensors_battery()

        bat_str = (
            f"{batterie.percent:.0f}% ({'En charge' if batterie.power_plugged else 'Sur batterie'})"
            if batterie
            else "Secteur"
        )

        return (
            f"Diagnostic système complet :\n"
            f"  • Système      : {os_info}\n"
            f"  • Processeur   : {cpu:.1f}% d'utilisation\n"
            f"  • Mémoire RAM  : {ram.percent:.1f}% utilisée ({ram.used // (1024**2)} Mo / {ram.total // (1024**2)} Mo)\n"
            f"  • Disque dur   : {disque.percent:.1f}% occupé ({disque.free // (1024**3)} Go libres)\n"
            f"  • Alimentation : {bat_str}"
        )

    def lancer_scraping_amazon(self) -> str:
        """Lance le pipeline complet du scraper Amazon et retourne un résumé vocal."""
        depot = self.controleur_scraping.executer(
            categories=config.CATEGORIES_PAR_DEFAUT,
            pages_par_categorie=1,
            filtre_marque="iphone",
        )
        stats = depot.obtenir_statistiques()
        self.envoyer_notification(
            "Jarvis — Scraping Terminé",
            f"{stats['total_produits']} produits extraits. Prix moyen : {stats['prix_moyen']} €",
        )
        return (
            f"Scraping Amazon terminé avec succès. "
            f"J'ai collecté {stats['total_produits']} produits dans {len(stats['nombre_par_categorie'])} catégories. "
            f"Le prix moyen est de {stats['prix_moyen']:.2f} euros et le prix maximum est de {stats['prix_maximum']:.2f} euros."
        )

    def lire_statistiques_marche(self) -> str:
        """Retourne les 3 statistiques de l'étude de marché."""
        if len(self.controleur_scraping.depot) == 0:
            self.controleur_scraping.executer()
        stats = self.controleur_scraping.depot.obtenir_statistiques()
        prod_max = stats.get("produit_maximum")
        nom_max = prod_max.titre if prod_max else "N/A"
        cats = ", ".join(
            f"{c} ({n})" for c, n in stats["nombre_par_categorie"].items()
        )
        return (
            f"Voici les 3 statistiques de l'étude de marché :\n"
            f"  1. Moyenne des prix      : {stats['prix_moyen']:.2f} € (Note moyenne : {stats['note_moyenne']}/5)\n"
            f"  2. Prix maximum          : {stats['prix_maximum']:.2f} € ({nom_max})\n"
            f"  3. Nombre par catégorie  : {cats}"
        )

    def filtrer_marque(self, marque: str) -> str:
        """Filtre les produits du dépôt selon une marque donnée."""
        if len(self.controleur_scraping.depot) == 0:
            self.controleur_scraping.executer(filtre_marque=marque)
        resultats = self.controleur_scraping.depot.filtrer_par_marque(marque)
        if not resultats:
            return f"Aucun produit trouvé pour la marque '{marque}'."
        lignes = [f"J'ai trouvé {len(resultats)} produit(s) pour la marque '{marque}' :"]
        for idx, p in enumerate(resultats, start=1):
            lignes.append(f"  {idx}. {p.titre} — {p.prix:.2f} € (Note : {p.note}/5)")
        return "\n".join(lignes)

    def ouvrir_url(self, url: str, nom_site: str) -> str:
        """Ouvre une URL dans le navigateur du système."""
        if shutil.which("xdg-open"):
            try:
                subprocess.Popen(
                    ["xdg-open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass
        return f"Ouverture de {nom_site} ({url}) dans votre navigateur."

    def rechercher_google(self, requete: str) -> str:
        """Lance une recherche Google sur le terme demandé."""
        terme = requete.strip() or "Python Web Scraping"
        url = f"https://www.google.com/search?q={quote_plus(terme)}"
        return self.ouvrir_url(url, f"la recherche Google '{terme}'")

    def envoyer_notification(self, titre: str, message: str) -> None:
        """Envoie une notification bureau sur Ubuntu via notify-send."""
        if shutil.which("notify-send"):
            try:
                subprocess.Popen(
                    ["notify-send", titre, message],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

