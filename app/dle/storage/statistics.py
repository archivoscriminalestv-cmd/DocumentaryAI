"""Construcción de estadísticas agregadas del documental (determinista)."""

from app.dle.analysis import editing, pacing
from app.dle.models import SceneSegment, ShotAnalysis, Statistics
from app.dle.storage.embeddings import build_embedding


def _distribution(shots: list[ShotAnalysis], attr: str) -> dict:
    out: dict = {}
    for s in shots:
        key = str(getattr(s, attr))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def build_statistics(shots: list[ShotAnalysis], scenes: list[SceneSegment],
                     duration: float) -> Statistics:
    lengths = pacing.shot_length_stats(shots)
    cpm = editing.cuts_per_minute(shots, duration)
    close_ups = sum(1 for s in shots if s.shot_size in ("close", "extreme close"))
    return Statistics(
        shot_count=len(shots), scene_count=len(scenes), cut_count=editing.cut_count(shots),
        average_shot_length=lengths["average"], median_shot_length=lengths["median"],
        min_shot_length=lengths["min"], max_shot_length=lengths["max"],
        cuts_per_minute=cpm, pacing_tier=lengths["tier"],
        shot_size_distribution=_distribution(shots, "shot_size"),
        movement_distribution=_distribution(shots, "movement"),
        lighting_distribution=_distribution(shots, "lighting"),
        color_temperature_distribution=_distribution(shots, "color_temperature"),
        dominant_color_distribution=_distribution(shots, "dominant_color"),
        close_up_frequency=round(close_ups / len(shots), 4) if shots else 0.0,
        time_with_audio=editing.time_where(shots, "audio_present", "true"),
        time_with_narration=editing.time_where(shots, "narration_present", "true"),
        time_with_music=editing.time_where(shots, "music_present", "true"),
        embedding=build_embedding(shots, lengths["average"], cpm),
    )
