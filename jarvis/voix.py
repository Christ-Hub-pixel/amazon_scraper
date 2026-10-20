"""
Module Vocal de J.A.R.V.I.S. (Synthèse vocale TTS & Reconnaissance vocale STT).
Utilise les outils natifs Linux (spd-say, arecord, aplay) et SpeechRecognition / pyttsx3.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

try:
    import speech_recognition as sr
except ImportError:
    sr = None  # type: ignore

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None  # type: ignore


class MoteurVocal:
    """Gère la voix (Text-To-Speech) et l'écoute microphone (Speech-To-Text) de Jarvis."""

    def __init__(self, activer_voix: bool = True, langue: str = "fr-FR") -> None:
        self.activer_voix = activer_voix
        self.langue = langue
        self.a_spd_say = bool(shutil.which("spd-say"))
        self.a_espeak = bool(shutil.which("espeak-ng") or shutil.which("espeak"))
        self.a_arecord = bool(shutil.which("arecord"))
        self._moteur_pyttsx3 = None

        if pyttsx3 is not None and not self.a_spd_say and self.a_espeak:
            try:
                self._moteur_pyttsx3 = pyttsx3.init()
                self._moteur_pyttsx3.setProperty("rate", 165)
            except Exception:
                self._moteur_pyttsx3 = None

    def parler(self, texte: str) -> None:
        """Prononce le texte à haute voix en français sans bloquer l'interface."""
        if not self.activer_voix or not texte.strip():
            return

        # Nettoyage des caractères de formatage avant synthèse vocale
        texte_propre = (
            texte.replace("*", "")
            .replace("#", "")
            .replace("`", "")
            .replace("•", "")
            .strip()
        )

        # 1. Speech Dispatcher natif Linux (spd-say)
        if self.a_spd_say:
            try:
                subprocess.Popen(
                    ["spd-say", "-l", "fr", "-r", "-5", texte_propre[:400]],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except Exception:
                pass

        # 2. pyttsx3 si disponible
        if self._moteur_pyttsx3 is not None:
            try:
                self._moteur_pyttsx3.say(texte_propre[:400])
                self._moteur_pyttsx3.runAndWait()
                return
            except Exception:
                pass

        # 3. espeak-ng / espeak direct
        binaire_espeak = shutil.which("espeak-ng") or shutil.which("espeak")
        if binaire_espeak:
            try:
                subprocess.Popen(
                    [binaire_espeak, "-v", "fr", texte_propre[:400]],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    def ecouter_microphone(self, duree_secondes: int = 4) -> Optional[str]:
        """
        Enregistre la voix via ALSA (arecord) et la transcrit en texte français
        avec Google Speech Recognition.
        """
        if not self.a_arecord or sr is None:
            return None

        fichier_wav = Path(tempfile.gettempdir()) / "jarvis_micro.wav"
        try:
            proc = subprocess.run(
                [
                    "arecord",
                    "-q",
                    "-d",
                    str(duree_secondes),
                    "-f",
                    "S16_LE",
                    "-r",
                    "16000",
                    "-c",
                    "1",
                    str(fichier_wav),
                ],
                timeout=duree_secondes + 3,
                check=False,
            )
            if proc.returncode != 0 or not fichier_wav.exists():
                return None

            recognizer = sr.Recognizer()
            with sr.AudioFile(str(fichier_wav)) as source:
                audio = recognizer.record(source)

            texte = recognizer.recognize_google(audio, language=self.langue)
            return str(texte).strip()
        except Exception:
            return None
        finally:
            if fichier_wav.exists():
                try:
                    fichier_wav.unlink()
                except Exception:
                    pass
