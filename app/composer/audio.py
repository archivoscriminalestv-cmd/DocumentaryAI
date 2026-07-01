"""Audio del Composer: narración sincronizada + cama musical + mezcla.

Garantiza ``timeline_audio == timeline_video``: la narración de cada escena se ajusta
EXACTAMENTE a la duración de su escena (acelerando si sobra texto, rellenando silencio
si falta), de modo que la suma total coincide con el vídeo. La música va por debajo de
la voz (voz prioritaria) con fundidos suaves.
"""

import os
import re
import subprocess
import tempfile

import imageio_ffmpeg

_SR = 44100
_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")
_MUSIC_VOLUME = 0.12   # voz prioritaria: la cama musical va baja
_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, timeout=600)
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", "replace")[-1200:]
        raise RuntimeError(f"FFmpeg audio failed: {' '.join(cmd[:6])}…\n{stderr}")


def media_duration(path: str) -> float:
    result = subprocess.run([_FFMPEG, "-i", path], capture_output=True, text=True, timeout=60)
    m = _DURATION_RE.search(result.stderr or "")
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def _silence(out_wav: str, duration: float) -> str:
    _run([_FFMPEG, "-y", "-f", "lavfi", "-i",
          f"anullsrc=channel_layout=stereo:sample_rate={_SR}",
          "-t", f"{max(0.1, duration):.3f}", "-c:a", "pcm_s16le", out_wav])
    return out_wav


def _fit(in_wav: str, target: float, out_wav: str) -> str:
    """Ajusta ``in_wav`` a EXACTAMENTE ``target`` s (acelera si sobra, rellena si falta)."""
    d = media_duration(in_wav)
    if d <= 0.05:
        return _silence(out_wav, target)
    filters = []
    if d > target + 0.05:                       # sobra voz -> acelerar (cap x2) y recortar
        tempo = min(2.0, d / target)
        filters.append(f"atempo={tempo:.4f}")
    # rellena con silencio y recorta a la duración exacta
    filters.append("apad")
    _run([_FFMPEG, "-y", "-i", in_wav, "-af", ",".join(filters),
          "-t", f"{target:.3f}", "-ar", str(_SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])
    return out_wav


def _concat(wavs: list[str], out_wav: str, tmp: str) -> str:
    list_path = os.path.join(tmp, "alist.txt")
    with open(list_path, "w", encoding="utf-8") as h:
        for w in wavs:
            h.write(f"file '{w.replace(chr(92), '/')}'\n")
    _run([_FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
          "-ar", str(_SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])
    return out_wav


class AudioComposer:
    """Construye la pista de audio final del documental, sincronizada al vídeo."""

    def __init__(self, synthesizer=None) -> None:
        self._synth = synthesizer
        self.narration_provider = type(synthesizer).__name__ if synthesizer else "none"
        self.music_provider = ""

    def build_narration(self, scene_plan: list[tuple], out_wav: str, tmp: str) -> str:
        """``scene_plan`` = [(scene_id, text, scene_duration), …] en orden de timeline."""
        segments = []
        for i, (scene_id, text, dur) in enumerate(scene_plan):
            seg = os.path.join(tmp, f"narr_{i:02d}.wav")
            raw = os.path.join(tmp, f"raw_{i:02d}.wav")
            ok = False
            if self._synth and text.strip():
                try:
                    ok = bool(self._synth.synthesize(text, raw))
                except Exception:
                    ok = False
            segments.append(_fit(raw, dur, seg) if ok else _silence(seg, dur))
        return _concat(segments, out_wav, tmp)

    def build_music(self, out_wav: str, total: float, music_path: str | None) -> str:
        fade = min(2.0, total / 4)
        if music_path and os.path.exists(music_path):
            self.music_provider = f"track:{os.path.basename(music_path)}"
            # loop + recorte + fundidos + volumen bajo
            _run([_FFMPEG, "-y", "-stream_loop", "-1", "-i", music_path,
                  "-t", f"{total:.3f}",
                  "-af", f"volume={_MUSIC_VOLUME},afade=t=in:st=0:d={fade:.2f},"
                         f"afade=t=out:st={max(0, total - fade):.2f}:d={fade:.2f}",
                  "-ar", str(_SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])
        else:
            # No hay pista musical: cama ambiental GENERADA (ruido marrón filtrado, bajo).
            self.music_provider = "generated:ambient-bed"
            _run([_FFMPEG, "-y", "-f", "lavfi",
                  "-i", f"anoisesrc=color=brown:sample_rate={_SR}:amplitude=0.05",
                  "-t", f"{total:.3f}",
                  "-af", f"lowpass=f=380,volume={_MUSIC_VOLUME},afade=t=in:st=0:d={fade:.2f},"
                         f"afade=t=out:st={max(0, total - fade):.2f}:d={fade:.2f}",
                  "-ar", str(_SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])
        return out_wav

    def mix(self, narration_wav: str, music_wav: str, out_wav: str, total: float) -> str:
        # Voz prioritaria (peso 1) + música (ya atenuada) -> duración exacta.
        _run([_FFMPEG, "-y", "-i", narration_wav, "-i", music_wav,
              "-filter_complex",
              "[0:a]volume=1.0[v];[1:a]volume=1.0[m];[v][m]amix=inputs=2:duration=first:"
              "dropout_transition=0:normalize=0[a]",
              "-map", "[a]", "-t", f"{total:.3f}",
              "-ar", str(_SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])
        return out_wav
