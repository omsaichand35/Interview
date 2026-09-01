"""
InterviewOS Voice Engine
Provides bidirectional Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities.
"""
import re
import threading
from typing import Optional

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

from rich.console import Console

console = Console()


def _clean_text_for_speech(text: str) -> str:
    """Strip markdown formatting, URLs, and code brackets for natural speech."""
    # Remove code blocks ```...```
    text = re.sub(r"```.*?```", "code snippet omitted", text, flags=re.DOTALL)
    # Remove inline code `...`
    text = re.sub(r"`(.*?)`", r"\1", text)
    # Remove markdown headers and bold/italics
    text = re.sub(r"[*#_~]", "", text)
    # Remove rich formatting tags [bold cyan] etc
    text = re.sub(r"\[.*?\]", "", text)
    # Remove URL links
    text = re.sub(r"https?://\S+", "", text)
    return text.strip()


class VoiceEngine:
    """Bidirectional Voice Engine for InterviewOS."""

    def __init__(self, rate: int = 175, volume: float = 0.95):
        self.rate = rate
        self.volume = volume
        self._engine = None
        self._recognizer = None
        self._is_speaking = False

    def _get_tts_engine(self):
        if self._engine is None and HAS_PYTTSX3:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", self.rate)
                self._engine.setProperty("volume", self.volume)
                # Select a clean natural voice if available
                voices = self._engine.getProperty("voices")
                if voices:
                    self._engine.setProperty("voice", voices[0].id)
            except Exception:
                self._engine = None
        return self._engine

    def _get_recognizer(self):
        if self._recognizer is None and HAS_SR:
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
        return self._recognizer

    def speak(self, text: str, block: bool = False) -> None:
        """
        Synthesize and speak text via Text-to-Speech (TTS).
        By default runs in background thread so UI is not blocked.
        """
        clean_text = _clean_text_for_speech(text)
        if not clean_text:
            return

        def _do_speak():
            try:
                engine = self._get_tts_engine()
                if engine:
                    self._is_speaking = True
                    engine.say(clean_text)
                    engine.runAndWait()
                    self._is_speaking = False
            except Exception:
                self._is_speaking = False

        if block:
            _do_speak()
        else:
            t = threading.Thread(target=_do_speak, daemon=True)
            t.start()

    def listen(self, timeout: int = 8, phrase_time_limit: int = 40) -> Optional[str]:
        """
        Record candidate audio from microphone and transcribe via Speech-to-Text (STT).
        Returns transcribed string or None on timeout/error.
        """
        if not HAS_SR:
            return None

        recognizer = self._get_recognizer()
        if not recognizer:
            return None

        try:
            with sr.Microphone() as source:
                console.print("[dim cyan]🎙 Calibrating microphone for ambient noise...[/dim cyan]")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                console.print("[bold green]🎙 [Listening] Speak your answer now... (or press Ctrl+C to type)[/bold green]")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            with console.status("[bold cyan]🔄 Transcribing voice audio to text...[/bold cyan]", spinner="dots"):
                text = recognizer.recognize_google(audio)
                return text.strip()

        except sr.WaitTimeoutError:
            console.print("[dim yellow]⚠ No speech detected within timeout period.[/dim yellow]")
            return None
        except sr.UnknownValueError:
            console.print("[dim yellow]⚠ Could not decipher audio cleanly.[/dim yellow]")
            return None
        except Exception as e:
            console.print(f"[dim yellow]⚠ Voice input unavailable: {e}[/dim yellow]")
            return None


# Global singleton instance
_default_voice_engine: Optional[VoiceEngine] = None

def get_voice_engine() -> VoiceEngine:
    global _default_voice_engine
    if _default_voice_engine is None:
        _default_voice_engine = VoiceEngine()
    return _default_voice_engine
