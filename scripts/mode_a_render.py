"""MODE A — Minimal Viable Render Engine (system test, ejecutable).

Consume MGL_SHOTS + NARRATION_ES y produce un MP4 real:
    output/final/documentary.mp4

Pasos: Asset Resolver (+fallback gray.mp4) -> Shot Renderer (FFmpeg, 1920x1080,
slow zoom, -t) -> Audio Engine (TTS es-ES local; fallback silencio) -> Timeline
Composer (concat + narración). Sin pseudo-código: llamadas FFmpeg por subprocess.
"""

import os
import subprocess

import imageio_ffmpeg

from app.infrastructure.visual.card_renderer import CardImageRenderer
from app.infrastructure.voice.sapi_synthesizer import SapiSpeechSynthesizer

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30

ROOT = os.getcwd()
ASSETS_DIR = os.path.join("output", "shots_assets")
FALLBACK = os.path.join("assets", "fallback", "gray.mp4")
SHOTS_DIR = os.path.join("output", "shots")
FINAL_DIR = os.path.join("output", "final")
AUDIO_WAV = os.path.join("output", "audio.wav")
FINAL_MP4 = os.path.join(FINAL_DIR, "documentary.mp4")

# (shot_id, duration_s, short_description) — suma de duraciones = 300s.
MGL_SHOTS = [
    ("S01", 6, "Trinitat Vella, Barcelona — anochecer"),
    ("S02", 8, "Calle vacia, farolas"),
    ("S03", 8, "Finestrelles x Almassora"),
    ("S04", 8, "La esquina (motivo)"),
    ("S05", 14, "Vida del barrio"),
    ("S06", 14, "Coquito (retrato simbolico)"),
    ("S07", 14, "Dos siluetas se cruzan"),
    ("S08", 8, "Tension (abstracto)"),
    ("S09", 12, "La discusion"),
    ("S10", 12, "Insertos de calle"),
    ("S11", 14, "Orbita del enfrentamiento"),
    ("S12", 16, "Testigos (siluetas)"),
    ("S13", 16, "Respiro antes del corte"),
    ("S14", 8, "El ataque (abstracto)"),
    ("S15", 10, "Silencio (negro)"),
    ("S16", 17, "Simulacion tipo CCTV"),
    ("S17", 14, "Luces de ambulancia"),
    ("S18", 13, "Hospital Vall d'Hebron"),
    ("S19", 13, "Muerte cerebral"),
    ("S20", 11, "Mapa de testigos"),
    ("S21", 12, "Repetidores moviles"),
    ("S22", 14, "Tablero de evidencias"),
    ("S23", 12, "Sala de justicia"),
    ("S24", 12, "Condena: 18 anos"),
    ("S25", 8, "Memoria del barrio"),
    ("S26", 6, "Cierre — atardecer"),
]

NARRATION_ES = (
    "El 4 de enero de 2021, una calle del barrio de Trinitat Vella, en Barcelona, "
    "se convirtio en el escenario de un crimen que sacudio a todo un vecindario. "
    "Lo que aquella tarde empezo como un encuentro entre conocidos termino, en cuestion "
    "de minutos, en una tragedia. Esta es la historia de Jonathan Burgos. En el barrio, "
    "todos lo conocian por un nombre: Coquito. "
    "Coquito tenia cuarenta anos. Era un vecino mas de Trinitat Vella, un rostro familiar "
    "en sus calles. Aquel dia, su camino se cruzo con el de un conocido. No era un "
    "desconocido: entre ellos, segun la investigacion, existian conflictos previos. Ya "
    "habian discutido antes. "
    "El reencuentro reavivo una tension que venia de lejos. En el cruce de las calles "
    "Finestrelles y Almassora, una nueva discusion empezo a subir de tono. Las voces se "
    "elevaron. La distancia entre ambos se fue acortando. Y entonces, las palabras dieron "
    "paso a algo que ya no tendria vuelta atras. "
    "Fue un ataque con arma blanca. Una unica punalada, dirigida al pecho. Varias personas "
    "lo presenciaron. Y, sobre todo, una camara lo registro. Aquel video se convertiria mas "
    "tarde en la prueba clave de toda la investigacion. "
    "Coquito fue trasladado de urgencia al Hospital Vall d'Hebron, en estado critico. "
    "Durante horas, los medicos intentaron salvarle la vida. Pero el diagnostico fue "
    "demoledor: muerte cerebral. Poco despues, Jonathan Burgos fallecia. El barrio perdia "
    "a uno de los suyos. "
    "Los Mossos d'Esquadra abrieron la investigacion de inmediato. La reconstruccion se "
    "apoyo en tres pilares: los testimonios de quienes estaban alli, el rastro de los "
    "repetidores de telefonia movil, y el video del ataque. Pieza a pieza, el cerco se fue "
    "cerrando. El 6 de enero de 2021, apenas dos dias despues del crimen, el agresor fue "
    "detenido. "
    "El caso llego a juicio en noviembre de 2022, ante un tribunal del jurado. Se escucharon "
    "las pruebas. Se valoro cada detalle. Y llego el veredicto. Una condena: dieciocho anos "
    "de prision. "
    "Pero ninguna sentencia devuelve lo perdido. En Trinitat Vella, el nombre de Coquito "
    "sigue presente en la memoria del barrio. Para su familia, el 4 de enero de 2021 nunca "
    "sera una simple fecha en un expediente. Es el dia en que todo cambio. La vida de "
    "Jonathan Burgos, una vida que su barrio no olvida."
)


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed (rc={result.returncode}): {' '.join(cmd)}\n"
            + (result.stderr or b"").decode("utf-8", "replace")[-600:]
        )


def ensure_dirs() -> None:
    for d in (ASSETS_DIR, os.path.dirname(FALLBACK), SHOTS_DIR, FINAL_DIR):
        os.makedirs(d, exist_ok=True)


def build_fallback() -> None:
    if os.path.exists(FALLBACK) and os.path.getsize(FALLBACK) > 0:
        return
    _run([FFMPEG, "-y", "-f", "lavfi", "-i", f"color=c=gray:s={W}x{H}:d=2",
          "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", FALLBACK])


def build_assets() -> None:
    """Genera una tarjeta por shot (estos son los 'assets' que el resolver usará)."""
    renderer = CardImageRenderer()
    for shot_id, _dur, desc in MGL_SHOTS:
        path = os.path.join(ASSETS_DIR, f"{shot_id}.png")
        renderer.render(desc, path, subtitle=shot_id)


def resolve_asset(shot_id: str) -> str:
    """Asset Resolver: usa el asset si existe; si no, el fallback gray.mp4."""
    candidate = os.path.join(ASSETS_DIR, f"{shot_id}.png")
    if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
        return candidate
    return FALLBACK


def render_shot(shot_id: str, duration: int) -> str:
    src = resolve_asset(shot_id)
    out = os.path.join(SHOTS_DIR, f"{shot_id}.mp4")
    frames = int(duration * FPS)
    if src.lower().endswith(".mp4"):  # fallback de vídeo (gray): escala + trim
        vf = f"scale={W}:{H},format=yuv420p"
        cmd = [FFMPEG, "-y", "-i", src, "-t", str(duration), "-vf", vf,
               "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", out]
    else:  # imagen: loop + slow zoom (zoompan)
        vf = (
            f"scale={W}:{H},"
            f"zoompan=z='min(zoom+0.0008,1.2)':d={frames}:s={W}x{H}:fps={FPS},"
            "format=yuv420p"
        )
        cmd = [FFMPEG, "-y", "-loop", "1", "-i", src, "-t", str(duration), "-vf", vf,
               "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", out]
    _run(cmd)
    print(f"  [shot] {shot_id} ({duration}s) <- {os.path.basename(src)} -> {out}")
    return out


def build_audio() -> bool:
    """Audio Engine: TTS es-ES (SAPI). Fallback: pista de silencio (300s)."""
    os.makedirs(os.path.dirname(os.path.abspath(AUDIO_WAV)), exist_ok=True)
    ok = SapiSpeechSynthesizer().synthesize(NARRATION_ES, AUDIO_WAV)
    if ok and os.path.exists(AUDIO_WAV) and os.path.getsize(AUDIO_WAV) > 0:
        print(f"  [audio] TTS local -> {AUDIO_WAV}")
        return True
    _run([FFMPEG, "-y", "-f", "lavfi",
          "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
          "-t", "300", "-c:a", "pcm_s16le", AUDIO_WAV])
    print(f"  [audio] TTS no disponible -> silencio (fallback) -> {AUDIO_WAV}")
    return False


def compose(shot_clips: list[str]) -> None:
    list_path = os.path.join(SHOTS_DIR, "concat.txt")
    with open(list_path, "w", encoding="utf-8") as handle:
        for clip in shot_clips:
            safe = os.path.abspath(clip).replace("\\", "/").replace("'", "'\\''")
            handle.write(f"file '{safe}'\n")

    silent = os.path.join(SHOTS_DIR, "_timeline_silent.mp4")
    _run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
          "-c:v", "copy", silent])  # vídeo concatenado (sin audio)

    # Mux narración. Sin -shortest: el vídeo (300s) define la duración.
    _run([FFMPEG, "-y", "-i", silent, "-i", AUDIO_WAV,
          "-map", "0:v:0", "-map", "1:a:0",
          "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
          FINAL_MP4])


def main() -> None:
    import sys
    try:  # consola Windows cp1252: aseguramos UTF-8 para el símbolo de OK
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("MODE A — Minimal Viable Render Engine")
    ensure_dirs()
    build_fallback()
    print(f"  [fallback] {FALLBACK}")
    build_assets()
    print(f"  [assets] {len(MGL_SHOTS)} tarjetas en {ASSETS_DIR}")
    clips = [render_shot(sid, dur) for sid, dur, _ in MGL_SHOTS]
    build_audio()
    compose(clips)
    print()
    print("✔ Render complete")
    print("✔ Output file:")
    print(FINAL_MP4.replace("\\", "/"))


if __name__ == "__main__":
    main()
