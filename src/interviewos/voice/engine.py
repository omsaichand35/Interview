"""
InterviewOS Voice Engine
Provides bidirectional Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities.
"""
import os
import re
import sys
import threading
from typing import Optional

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

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
        self._win_speaker = None
        self._is_speaking = False

    def _get_recognizer(self):
        if self._recognizer is None and HAS_SR:
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 280
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8
            self._recognizer.phrase_threshold = 0.3
        return self._recognizer

    def speak(self, text: str, block: bool = False) -> None:
        """
        Synthesize and speak text via Text-to-Speech (TTS).
        Uses native Windows SAPI asynchronously or pyttsx3.
        """
        clean_text = _clean_text_for_speech(text)
        if not clean_text:
            return

        def _do_speak():
            try:
                # Primary Windows Native SAPI
                if os.name == "nt" and HAS_WIN32COM:
                    import pythoncom
                    pythoncom.CoInitialize()
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Volume = int(self.volume * 100)
                    speaker.Rate = 1 # Normal conversational pace
                    # 0 = synchronous within this worker thread
                    speaker.Speak(clean_text, 0)
                    pythoncom.CoUninitialize()
                    return
            except Exception:
                pass

            # Fallback to pyttsx3
            try:
                if HAS_PYTTSX3:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", self.rate)
                    engine.setProperty("volume", self.volume)
                    engine.say(clean_text)
                    engine.runAndWait()
            except Exception:
                pass

        if block:
            _do_speak()
        else:
            t = threading.Thread(target=_do_speak, daemon=True)
            t.start()

    def listen(self, timeout: int = 10, phrase_time_limit: int = 45) -> Optional[str]:
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
                console.print("[dim cyan]🎙 Calibrating microphone for room acoustics...[/dim cyan]")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                console.print("[bold green]🎙 [Listening] Speak your answer now... (or press Ctrl+C to switch to typing)[/bold green]")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            with console.status("[bold cyan]🔄 Transcribing voice audio to text...[/bold cyan]", spinner="dots"):
                text = recognizer.recognize_google(audio)
                return text.strip()

        except sr.WaitTimeoutError:
            console.print("[dim yellow]⚠ No speech detected (switching to keyboard typing).[/dim yellow]")
            return None
        except sr.UnknownValueError:
            console.print("[dim yellow]⚠ Speech audio unclear (switching to keyboard typing).[/dim yellow]")
            return None
        except Exception as e:
            console.print(f"[dim yellow]⚠ Microphone input note: {e}[/dim yellow]")
            return None


# Global singleton instance
_default_voice_engine: Optional[VoiceEngine] = None

def get_voice_engine() -> VoiceEngine:
    global _default_voice_engine
    if _default_voice_engine is None:
        _default_voice_engine = VoiceEngine()
    return _default_voice_engine
