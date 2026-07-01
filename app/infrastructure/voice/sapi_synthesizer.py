"""SapiSpeechSynthesizer — locución local en Windows vía System.Speech (SAPI).

Encapsula la única dependencia de plataforma para TTS: invoca PowerShell para
sintetizar un WAV con la voz instalada en el sistema. No requiere claves ni red.
Degrada con elegancia: si SAPI no está disponible o falla, devuelve False y el
caller continúa el pipeline sin audio real.

El dominio/aplicación no conocen PowerShell ni SAPI (ARCH-0002 AP-006).
"""

import os
import subprocess
import tempfile


class SapiSpeechSynthesizer:
    def __init__(self, rate: int = 0) -> None:
        # rate: -10..10 (System.Speech); 0 es velocidad natural.
        self._rate = rate

    def synthesize(self, text: str, out_path: str) -> bool:
        text = text.strip()
        if not text:
            return False

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

        # Pasamos el texto por fichero UTF-8 para no pelearnos con el quoting ni
        # con los acentos en la línea de comandos de Windows.
        txt_fd, txt_path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(txt_fd, "w", encoding="utf-8") as handle:
                handle.write(text)

            script = (
                "Add-Type -AssemblyName System.Speech;"
                "$t = [IO.File]::ReadAllText('{txt}', "
                "[Text.Encoding]::UTF8);"
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                "$s.Rate = {rate};"
                "$s.SetOutputToWaveFile('{wav}');"
                "$s.Speak($t);"
                "$s.Dispose()"
            ).format(
                txt=txt_path.replace("'", "''"),
                rate=self._rate,
                wav=os.path.abspath(out_path).replace("'", "''"),
            )

            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                timeout=120,
            )
            if result.returncode != 0:
                return False
        except Exception:
            return False
        finally:
            try:
                os.remove(txt_path)
            except OSError:
                pass

        return os.path.exists(out_path) and os.path.getsize(out_path) > 0
