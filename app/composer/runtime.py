"""DocumentaryComposer — runtime end-to-end que produce el MP4 final.

Consume contratos públicos (asset paths del ALR, MotionShots del CME, narración,
música, timeline) y EJECUTA: por cada plano genera un clip con movimiento; ensambla
los clips; construye y sincroniza el audio; aplica transiciones; produce
``documentary.mp4`` + ``composer_manifest.json`` + ``composer_report.md``.

El Composer no decide nada cinematográfico: solo ejecuta lo ya planificado.
"""

import json
import os
import subprocess
import tempfile
import time

import imageio_ffmpeg

from app.composer import transitions
from app.composer.audio import AudioComposer, media_duration
from app.composer.ffmpeg_motion_executor import FFmpegMotionExecutor
from app.composer.models import ClipResult, ComposerResult

_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, timeout=900)
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", "replace")[-1500:]
        raise RuntimeError(f"FFmpeg failed: {' '.join(cmd[:6])}…\n{stderr}")


class DocumentaryComposer:
    def __init__(self, *, executor=None, synthesizer=None, fps: int = 25,
                 width: int = 1280, height: int = 720) -> None:
        self.executor = executor or FFmpegMotionExecutor(fps=fps, width=width, height=height)
        self.audio = AudioComposer(synthesizer=synthesizer)
        self.fps, self.width, self.height = fps, width, height

    def run(self, *, motion_shots: list, asset_paths: list[str],
            narration_by_scene: dict[str, str], output_dir: str, project: str = "documentary",
            music_path: str | None = None, cache_hits: int = 0) -> ComposerResult:
        started = time.perf_counter()
        clips_dir = os.path.join(output_dir, "clips")
        os.makedirs(clips_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "documentary.mp4")
        total = len(motion_shots)

        clips: list[ClipResult] = []
        transitions_used: dict[str, int] = {}
        motions_used: dict[str, int] = {}

        # 1) Un clip MP4 con movimiento por plano.
        for i, (shot, asset) in enumerate(zip(motion_shots, asset_paths)):
            tdec = transitions.decide(i, total)
            clip_path = os.path.join(clips_dir, f"clip_{i + 1:03d}.mp4")
            params = shot.parameters.to_dict() if hasattr(shot.parameters, "to_dict") else dict(shot.parameters)
            self.executor.execute(
                asset_path=asset, motion_type=shot.motion_type, parameters=params,
                duration=shot.duration, out_clip=clip_path,
                fade_in=tdec["fade_in"], fade_out=tdec["fade_out"],
            )
            clips.append(ClipResult(
                index=i, shot_id=shot.shot_id, scene_id=shot.scene_id, asset_id=shot.asset_id,
                motion_type=shot.motion_type, duration=round(float(shot.duration), 3),
                transition_in=tdec["transition_in"], transition_out=tdec["transition_out"],
                clip_path=clip_path, filter_summary=f"{shot.motion_type}/{params.get('easing', '')}",
            ))
            transitions_used[tdec["transition_in"]] = transitions_used.get(tdec["transition_in"], 0) + 1
            motions_used[shot.motion_type] = motions_used.get(shot.motion_type, 0) + 1

        with tempfile.TemporaryDirectory() as tmp:
            # 2) Vídeo maestro = concatenación de clips (uniformes -> copia).
            master = os.path.join(tmp, "master.mp4")
            self._concat([c.clip_path for c in clips], master, tmp)
            video_duration = media_duration(master)

            # 3) Narración por escena ajustada a la duración de cada escena (sincronía exacta).
            scene_plan = self._scene_plan(clips, narration_by_scene)
            narration = self.audio.build_narration(scene_plan, os.path.join(tmp, "narr.wav"), tmp)
            # 4) Música (cama) + 5) mezcla voz-prioritaria, a la duración exacta del vídeo.
            music = self.audio.build_music(os.path.join(tmp, "music.wav"), video_duration, music_path)
            final_audio = self.audio.mix(narration, music, os.path.join(tmp, "final.wav"), video_duration)
            audio_duration = media_duration(final_audio)

            # 6) Mux: vídeo + audio -> documentary.mp4 (mismas duraciones).
            self._mux(master, final_audio, out_path)

        result = ComposerResult(
            project=project, output_path=out_path, clips=clips,
            total_duration=round(media_duration(out_path), 3),
            video_duration=round(video_duration, 3), audio_duration=round(audio_duration, 3),
            in_sync=abs(video_duration - audio_duration) <= 0.25,
            fps=self.fps, width=self.width, height=self.height,
            bitrate=self._bitrate(out_path), render_seconds=round(time.perf_counter() - started, 2),
            cache_hits=cache_hits, transitions_used=transitions_used, motions_used=motions_used,
            assets_used=[c.asset_id for c in clips],
            narration_provider=self.audio.narration_provider, music_provider=self.audio.music_provider,
        )
        self._write_outputs(output_dir, result)
        return result

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _scene_plan(clips: list[ClipResult], narration_by_scene: dict) -> list[tuple]:
        """[(scene_id, text, scene_duration)] en orden, sumando la duración de sus clips."""
        order, durations = [], {}
        for c in clips:
            if c.scene_id not in durations:
                order.append(c.scene_id)
                durations[c.scene_id] = 0.0
            durations[c.scene_id] += c.duration
        return [(sid, narration_by_scene.get(sid, ""), durations[sid]) for sid in order]

    def _concat(self, clips: list[str], out_path: str, tmp: str) -> None:
        list_path = os.path.join(tmp, "vlist.txt")
        with open(list_path, "w", encoding="utf-8") as h:
            for p in clips:
                h.write(f"file '{os.path.abspath(p).replace(chr(92), '/')}'\n")
        _run([_FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
              "-c", "copy", out_path])

    def _mux(self, video: str, audio: str, out_path: str) -> None:
        _run([_FFMPEG, "-y", "-i", video, "-i", audio,
              "-map", "0:v:0", "-map", "1:a:0",
              "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path])
        if not (os.path.exists(out_path) and os.path.getsize(out_path) > 0):
            raise RuntimeError(f"mux no produjo salida en {out_path}")

    @staticmethod
    def _bitrate(path: str) -> str:
        result = subprocess.run([_FFMPEG, "-i", path], capture_output=True, text=True, timeout=60)
        import re
        m = re.search(r"bitrate:\s*(\d+\s*kb/s)", result.stderr or "")
        return m.group(1) if m else ""

    def _write_outputs(self, output_dir: str, result: ComposerResult) -> None:
        with open(os.path.join(output_dir, "composer_manifest.json"), "w", encoding="utf-8") as h:
            json.dump(result.to_dict(), h, ensure_ascii=False, indent=2)
        with open(os.path.join(output_dir, "composer_report.md"), "w", encoding="utf-8") as h:
            h.write(_render_report(result))


def _render_report(r: ComposerResult) -> str:
    lines = [
        f"# Composer report — {r.project}",
        "",
        f"- **Output:** `{r.output_path}`",
        f"- **Total duration:** {r.total_duration:.2f}s",
        f"- **Video / Audio:** {r.video_duration:.2f}s / {r.audio_duration:.2f}s  ·  "
        f"**In sync:** {'yes' if r.in_sync else 'NO'}",
        f"- **Resolution / FPS:** {r.width}x{r.height} @ {r.fps}fps  ·  **Bitrate:** {r.bitrate or 'n/a'}",
        f"- **Clips:** {len(r.clips)}  ·  **Render time:** {r.render_seconds:.1f}s  ·  "
        f"**Cache hits (ALR):** {r.cache_hits}",
        f"- **Narration:** {r.narration_provider}  ·  **Music:** {r.music_provider}",
        f"- **Transitions used:** {r.transitions_used}",
        f"- **Motions executed:** {r.motions_used}",
        "",
        "## Per-clip",
        "",
        "| # | Clip | Shot | Scene | Asset | Motion | Dur (s) | In | Out |",
        "|---|------|------|-------|-------|--------|--------:|----|-----|",
    ]
    for c in r.clips:
        lines.append(
            f"| {c.index + 1} | {os.path.basename(c.clip_path)} | {c.shot_id} | {c.scene_id} | "
            f"{c.asset_id} | {c.motion_type} | {c.duration:.1f} | {c.transition_in} | {c.transition_out} |"
        )
    return "\n".join(lines) + "\n"
