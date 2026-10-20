"""
Cœur de l'assistant J.A.R.V.I.S. (Just A Rather Very Intelligent System).
Analyse les commandes vocales ou textuelles et exécute la compétence correspondante.
"""

import re
from typing import Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    Console = None  # type: ignore
    Panel = None  # type: ignore
    Table = None  # type: ignore

from jarvis.competences import CompetencesJarvis
from jarvis.voix import MoteurVocal


class JarvisAssistant:
    """Classe principale POO de l'assistant personnel J.A.R.V.I.S."""

    def __init__(self, activer_voix: bool = True) -> None:
        self.voix = MoteurVocal(activer_voix=activer_voix)
        self.competences = CompetencesJarvis()
        self.console = Console() if Console is not None else None

    def afficher_interface_accueil(self) -> None:
        """Affiche le tableau de bord J.A.R.V.I.S. dans le terminal."""
        if self.console and Panel and Table:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Commande vocale ou texte", style="bold yellow")
            table.add_column("Action exécutée par J.A.R.V.I.S.", style="white")
            table.add_row("scrape / lance le scraper", "Lance le scraping Amazon (3 pages, CSV, SQLite)")
            table.add_row("statistiques / étude de marché", "Affiche Moyenne, Maximum et Nombre par catégorie")
            table.add_row("filtre <marque> (ex: filtre iphone)", "Filtre uniquement les produits d'une marque")
            table.add_row("diagnostic / système / batterie", "Affiche l'état CPU, RAM, Disque et Batterie")
            table.add_row("heure / date", "Donne la date et l'heure exactes")
            table.add_row("ouvre github / ouvre amazon", "Ouvre votre dépôt GitHub ou Amazon dans le navigateur")
            table.add_row("cherche <sujet>", "Effectue une recherche Google")
            table.add_row("micro / écoute", "Active l'écoute vocale par microphone (4 secondes)")
            table.add_row("quitter / stop", "Arrête J.A.R.V.I.S.")

            self.console.print(
                Panel.fit(
                    "[bold cyan]J.A.R.V.I.S. v1.0.0[/bold cyan] — Assistant Vocal & IA (Connecté à Amazon Scraper)",
                    border_style="cyan",
                )
            )
            self.console.print(table)
        else:
            print("=" * 76)
            print("   J.A.R.V.I.S. v1.0.0 — ASSISTANT VOCAL & IA")
            print("=" * 76)

    def repondre(self, message: str, parler: bool = True) -> None:
        """Affiche la réponse de Jarvis et la prononce vocalement."""
        if self.console and Panel:
            self.console.print(
                Panel(message, title="[bold cyan]J.A.R.V.I.S.[/bold cyan]", border_style="blue")
            )
        else:
            print(f"\n[J.A.R.V.I.S.] : {message}\n")

        if parler:
            self.voix.parler(message)

    def traiter_commande(self, commande_brute: str) -> Tuple[str, bool]:
        """
        Analyse la requête de l'utilisateur et retourne (réponse, continuer_boucle).
        """
        cmd = commande_brute.strip().lower()
        if not cmd:
            return ("Je vous écoute Monsieur. Tapez 'aide' pour voir mes commandes.", True)

        # 1. Arrêt
        if cmd in {"quitter", "exit", "stop", "au revoir", "bye", "0"}:
            return ("Mise en veille des systèmes. À bientôt Monsieur.", False)

        # 2. Aide
        if "aide" in cmd or "help" in cmd or "que sais-tu faire" in cmd:
            return (
                "Je peux lancer le scraper Amazon ('scrape'), afficher les statistiques d'étude de marché "
                "('statistiques'), filtrer une marque ('filtre iphone'), vérifier l'état du PC ('diagnostic'), "
                "donner l'heure ('heure'), ouvrir votre GitHub ('ouvre github') ou faire une recherche ('cherche ...').",
                True,
            )

        # 3. Salutations
        if any(mot in cmd for mot in ("bonjour", "salut", "bonsoir", "hello", "coucou")):
            return (self.competences.obtenir_salutation(), True)

        # 4. Heure et date
        if any(mot in cmd for mot in ("heure", "date", "quel jour")):
            return (self.competences.donner_heure_et_date(), True)

        # 5. Diagnostic système
        if any(mot in cmd for mot in ("diagnostic", "système", "systeme", "cpu", "ram", "batterie", "état du pc")):
            return (self.competences.diagnostic_systeme(), True)

        # 6. Scraper Amazon
        if any(mot in cmd for mot in ("scrape", "scraper", "lance le scraping", "amazon scraper")):
            return (self.competences.lancer_scraping_amazon(), True)

        # 7. Statistiques étude de marché
        if any(mot in cmd for mot in ("statistique", "stats", "étude de marché", "etude de marche", "moyenne", "maximum")):
            return (self.competences.lire_statistiques_marche(), True)

        # 8. Filtre par marque (ex: "filtre iphone" ou "marque sony")
        match_filtre = re.search(r"(?:filtre|filtrer|marque)\s+(.+)", cmd)
        if match_filtre:
            marque = match_filtre.group(1).strip()
            return (self.competences.filtrer_marque(marque), True)
        if "iphone" in cmd:
            return (self.competences.filtrer_marque("iphone"), True)

        # 9. Ouverture de sites (GitHub, Amazon, YouTube)
        if "github" in cmd:
            return (
                self.competences.ouvrir_url(
                    "https://github.com/Christ-Hub-pixel/amazon_scraper",
                    "votre dépôt GitHub amazon_scraper",
                ),
                True,
            )
        if "youtube" in cmd:
            return (self.competences.ouvrir_url("https://www.youtube.com", "YouTube"), True)
        if "ouvre amazon" in cmd:
            return (self.competences.ouvrir_url("https://www.amazon.fr", "Amazon France"), True)

        # 10. Recherche Google
        match_recherche = re.search(r"(?:cherche|recherche|google)\s+(.+)", cmd)
        if match_recherche:
            sujet = match_recherche.group(1).strip()
            return (self.competences.rechercher_google(sujet), True)

        return (
            f"J'ai bien reçu la commande '{commande_brute}'. "
            "Tapez 'scrape', 'statistiques', 'filtre iphone', 'diagnostic', 'heure' ou 'ouvre github'.",
            True,
        )

    def demarrer_session_interactive(self) -> None:
        """Lance la boucle principale interactive (Voix + Clavier) de J.A.R.V.I.S."""
        self.afficher_interface_accueil()
        salutation = self.competences.obtenir_salutation()
        self.repondre(salutation)

        while True:
            try:
                entree = input("\n[Vous] (ou tapez 'micro' pour parler) > ").strip()
            except (EOFError, KeyboardInterrupt):
                self.repondre("Arrêt de J.A.R.V.I.S. À bientôt Monsieur.")
                break

            if entree.lower() in {"micro", "ecoute", "écoute", "voix"}:
                print("🎤 [J.A.R.V.I.S. vous écoute pendant 4 secondes... Parlez maintenant !]")
                texte_vocal = self.voix.ecouter_microphone(duree_secondes=4)
                if not texte_vocal:
                    self.repondre(
                        "Je n'ai pas pu capter votre voix via le microphone. Vous pouvez saisir votre commande au clavier."
                    )
                    continue
                print(f"🗣  Reconnu : '{texte_vocal}'")
                entree = texte_vocal

            reponse, continuer = self.traiter_commande(entree)
            self.repondre(reponse)
            if not continuer:
                break

