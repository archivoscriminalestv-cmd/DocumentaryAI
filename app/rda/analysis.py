"""Análisis puro del RDA: cortes, agregación por plano y mapeo a vocabulario.

Sin red, sin ffmpeg, sin IA: opera sobre ``list[FrameFeatures]`` ya extraídos.
El mapeo a etiquetas (pacing/lighting/color/movement) sigue ARCH-VIS-000 y usa
umbrales heurísticos DECLARADOS y ajustables (se calibran con las primeras
referencias). Esto es 100 % testable sin vídeo real.
"""

from statistics import median, pstdev

from app.rda.models import CinematicProfile, FrameFeatures, ShotProfile

# --- Umbrales (heurísticos, calibrables) -------------------------------------
CUT_THRESHOLD = 0.30        # diferencia de huella >= -> corte duro
MIN_SHOT_FRAMES = 2         # evita microplanos por destellos


def signature_diffs(frames: list[FrameFeatures]) -> list[float]:
    """Diferencia normalizada (0..1) de cada fotograma respecto al anterior."""
    diffs = [0.0]
    for i in range(1, len(frames)):
        a, b = frames[i - 1].signature, frames[i].signature
        if not a or not b or len(a) != len(b):
            diffs.append(0.0)
            continue
        diffs.append(sum(abs(x - y) for x, y in zip(a, b)) / (len(a) * 255.0))
    return diffs


def detect_boundaries(
    frames: list[FrameFeatures],
    *,
    threshold: float = CUT_THRESHOLD,
    min_shot_frames: int = MIN_SHOT_FRAMES,
) -> list[tuple[int, int]]:
    """Devuelve spans [start, end) de fotogramas por plano según cortes duros."""
    n = len(frames)
    if n == 0:
        return []
    diffs = signature_diffs(frames)
    cuts = [0]
    for i in range(1, n):
        if diffs[i] >= threshold and (i - cuts[-1]) >= min_shot_frames:
            cuts.append(i)
    spans = []
    for k, start in enumerate(cuts):
        end = cuts[k + 1] if k + 1 < len(cuts) else n
        spans.append((start, end))
    return spans


# --- Mapeo a vocabulario cinematográfico (ARCH-VIS-000) ----------------------

def pacing_tier(avg_shot_length: float) -> str:          # §6
    if avg_shot_length < 2.0:
        return "very_fast"
    if avg_shot_length < 3.5:
        return "fast"
    if avg_shot_length < 6.0:
        return "moderate"
    return "slow"


def variety_label(stddev: float, mean: float) -> str:    # §6.2 / §13.4
    cv = (stddev / mean) if mean > 0 else 0.0
    if cv < 0.30:
        return "metronomic"
    if cv < 0.70:
        return "moderate"
    return "varied"


def lighting_tendency(brightness: float, contrast: float) -> str:   # §4
    if brightness < 70:
        key = "low-key"
    elif brightness > 170:
        key = "high-key"
    else:
        key = "balanced"
    if contrast > 60:
        return f"{key} high-contrast"
    if contrast < 30:
        return f"{key} flat"
    return key


def color_temperature(warmth: float) -> str:             # §12 (grade)
    if warmth > 12:
        return "warm"
    if warmth < -12:
        return "cool"
    return "neutral"


def saturation_tendency(colorfulness: float) -> str:     # §12
    if colorfulness > 40:
        return "vivid"
    if colorfulness < 18:
        return "muted"
    return "moderate"


def movement_tendency(motion: float) -> str:             # §2 / §11
    if motion > 0.060:
        return "dynamic"
    if motion < 0.020:
        return "mostly_static"
    return "moderate"


def _aspect_ratio(width: int, height: int) -> str:
    if not width or not height:
        return "unknown"
    ratio = width / height
    for label, value in (("1:1", 1.0), ("4:3", 1.333), ("16:9", 1.777), ("1.85:1", 1.85), ("2.39:1", 2.39)):
        if abs(ratio - value) < 0.06:
            return label
    return f"{ratio:.2f}:1"


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_profile(
    reference: str,
    source_type: str,
    frames: list[FrameFeatures],
    *,
    sample_fps: float,
    meta: dict | None = None,
    threshold: float = CUT_THRESHOLD,
) -> CinematicProfile:
    """Construye el CinematicProfile a partir de los rasgos de fotograma."""
    meta = meta or {}
    interval = 1.0 / sample_fps if sample_fps > 0 else 0.0
    diffs = signature_diffs(frames)
    spans = detect_boundaries(frames, threshold=threshold)

    shots: list[ShotProfile] = []
    for index, (start, end) in enumerate(spans):
        block = frames[start:end]
        start_t = block[0].t
        end_t = block[-1].t + interval
        intra = diffs[start + 1:end]
        shots.append(
            ShotProfile(
                index=index,
                start=round(start_t, 3),
                end=round(end_t, 3),
                duration=round(end_t - start_t, 3),
                brightness=round(_mean([f.brightness for f in block]), 2),
                contrast=round(_mean([f.contrast for f in block]), 2),
                warmth=round(_mean([f.warmth for f in block]), 2),
                colorfulness=round(_mean([f.colorfulness for f in block]), 2),
                motion=round(_mean(intra), 4),
            )
        )

    durations = [s.duration for s in shots] or [0.0]
    duration = float(meta.get("duration") or (frames[-1].t + interval if frames else 0.0))
    minutes = duration / 60.0 if duration else 0.0

    asl = _mean(durations)
    sd = pstdev(durations) if len(durations) > 1 else 0.0
    brightness_mean = _mean([f.brightness for f in frames])
    contrast_mean = _mean([f.contrast for f in frames])
    warmth_mean = _mean([f.warmth for f in frames])
    colorfulness_mean = _mean([f.colorfulness for f in frames])
    motion_mean = _mean([s.motion for s in shots])

    profile = CinematicProfile(
        reference=reference,
        source_type=source_type,
        width=int(meta.get("width", 0)),
        height=int(meta.get("height", 0)),
        aspect_ratio=_aspect_ratio(int(meta.get("width", 0)), int(meta.get("height", 0))),
        fps=float(meta.get("fps", 0.0)),
        duration=round(duration, 2),
        sample_fps=sample_fps,
        shot_count=len(shots),
        avg_shot_length=round(asl, 3),
        median_shot_length=round(median(durations), 3),
        min_shot_length=round(min(durations), 3),
        max_shot_length=round(max(durations), 3),
        shot_length_stddev=round(sd, 3),
        cuts_per_minute=round((max(0, len(shots) - 1)) / minutes, 2) if minutes else 0.0,
        pacing_tier=pacing_tier(asl),
        shot_length_variety=variety_label(sd, asl),
        brightness_mean=round(brightness_mean, 2),
        contrast_mean=round(contrast_mean, 2),
        lighting_tendency=lighting_tendency(brightness_mean, contrast_mean),
        warmth_mean=round(warmth_mean, 2),
        colorfulness_mean=round(colorfulness_mean, 2),
        color_temperature=color_temperature(warmth_mean),
        saturation_tendency=saturation_tendency(colorfulness_mean),
        motion_mean=round(motion_mean, 4),
        movement_tendency=movement_tendency(motion_mean),
        shots=shots,
    )
    profile.grammar_notes = _grammar_notes(profile)
    profile.spec_alignment = _spec_alignment(profile)
    return profile


def _grammar_notes(p: CinematicProfile) -> list[str]:
    return [
        f"Average shot length {p.avg_shot_length:.1f}s -> {p.pacing_tier} editing "
        f"({p.cuts_per_minute:.0f} cuts/min, {p.shot_count} shots).",
        f"Shot-length variety: {p.shot_length_variety}.",
        f"Lighting tendency: {p.lighting_tendency} "
        f"(brightness {p.brightness_mean:.0f}, contrast {p.contrast_mean:.0f}).",
        f"Color grade: {p.color_temperature}, {p.saturation_tendency} "
        f"(warmth {p.warmth_mean:.0f}, colorfulness {p.colorfulness_mean:.0f}).",
        f"Camera/motion: {p.movement_tendency} (mean intra-shot motion {p.motion_mean:.3f}).",
    ]


def _spec_alignment(p: CinematicProfile) -> dict:
    # Conecta cada observación con la sección de ARCH-VIS-000 que rige.
    return {
        "§6 visual_pacing": f"{p.pacing_tier} (ASL {p.avg_shot_length:.1f}s)",
        "§13 shot_variety": p.shot_length_variety,
        "§4 lighting": p.lighting_tendency,
        "§12 color_grade": f"{p.color_temperature}/{p.saturation_tendency}",
        "§2_§11 camera_movement": p.movement_tendency,
        "§5 composition": p.aspect_ratio,
    }
