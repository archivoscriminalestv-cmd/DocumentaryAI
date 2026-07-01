"""Telemetría del VPL — informes a partir del GenerationManifest.

- ``build_report``     -> texto legible (consola).
- ``build_telemetry``  -> dict serializable (telemetry.json).
- ``build_render_report`` -> Markdown con tabla por plano (render_report.md).
"""


def _totals(manifest):
    generated = [a for a in manifest.assets if a.get("status") == "generated"]
    total_cost = sum(float(a.get("cost", 0.0)) for a in manifest.assets)
    times = [float(a.get("generation_time", 0.0)) for a in generated]
    avg = sum(times) / len(times) if times else 0.0
    return generated, total_cost, avg


def build_report(manifest) -> str:
    generated, total_cost, avg = _totals(manifest)

    lines = [
        "Documentary generated",
        "",
        f"Provider:           {manifest.provider}",
        f"Model:              {manifest.model}",
        f"Images:             {manifest.total}",
        f"Generated:          {manifest.cache_misses}",
        f"Cache reused:       {manifest.cache_hits}",
        f"Failures:           {manifest.failures}",
        f"Retries:            {manifest.retries}",
        f"Total cost:         ${total_cost:.4f}",
        f"Average generation: {avg:.2f}s",
        f"Total render time:  {manifest.duration_seconds:.2f}s",
    ]
    return "\n".join(lines)


def _provider_breakdown(manifest) -> dict:
    """Recuento de planos por proveedor que realmente los generó (incl. fallback)."""
    counts: dict[str, int] = {}
    for a in manifest.assets:
        winner = _winner(a) or "?"
        counts[winner] = counts.get(winner, 0) + 1
    return counts


def _reuse_ratio(manifest) -> float:
    return round(manifest.cache_hits / manifest.total, 3) if manifest.total else 0.0


def _winner(asset: dict) -> str:
    meta = asset.get("metadata", {}) or {}
    return meta.get("router_winner") or meta.get("chain_winner") or asset.get("provider", "")


def build_telemetry(manifest) -> dict:
    """Telemetría estructurada (telemetry.json)."""
    generated, total_cost, avg = _totals(manifest)
    return {
        "documentary_id": manifest.documentary_id,
        "provider": manifest.provider,
        "model": manifest.model,
        "timestamp": manifest.timestamp,
        "images": manifest.total,
        "generated": manifest.cache_misses,
        "cache_hits": manifest.cache_hits,
        "cache_misses": manifest.cache_misses,
        "reuse_ratio": _reuse_ratio(manifest),
        "failures": manifest.failures,
        "retries": manifest.retries,
        "total_cost": round(total_cost, 4),
        "average_generation_time": round(avg, 3),
        "total_render_time": manifest.duration_seconds,
        "provider_breakdown": _provider_breakdown(manifest),
        "shots": [
            {
                "shot_id": a.get("shot_id"),
                "scene": a.get("scene") or a.get("scene_id"),
                "provider": _winner(a),
                "model": a.get("model"),
                "generation_time": a.get("generation_time"),
                "cost": a.get("cost"),
                "resolution": a.get("resolution"),
                "hash": a.get("image_hash") or a.get("hash"),
                "seed": a.get("seed"),
                "reuse_key": a.get("reuse_key"),
                "cache": a.get("cache", a.get("cached")),
                "prompt": a.get("prompt"),
                "negative_prompt": a.get("negative_prompt"),
                "status": a.get("status"),
                "filename": a.get("filename"),
            }
            for a in manifest.assets
        ],
        "failed": [
            {"shot_id": f.get("shot_id"), "scene": f.get("scene_id"),
             "error": f.get("error"), "status": f.get("status")}
            for f in manifest.failed
        ],
    }


def _md_cell(text, limit: int = 60) -> str:
    return str(text or "").replace("|", "/").replace("\n", " ")[:limit]


def build_render_report(manifest) -> str:
    """Informe Markdown con tabla por plano + prompts (render_report.md)."""
    generated, total_cost, avg = _totals(manifest)
    breakdown = _provider_breakdown(manifest)
    breakdown_str = ", ".join(f"{k}: {v}" for k, v in breakdown.items()) or "—"
    reuse_ratio = _reuse_ratio(manifest)

    lines = [
        f"# Render report — {manifest.documentary_id}",
        "",
        f"- **Generated at:** {manifest.timestamp}",
        f"- **Strategy / provider:** `{manifest.provider}`",
        f"- **Images:** {manifest.total}  ·  **Generated:** {manifest.cache_misses}  ·  "
        f"**Cache hits:** {manifest.cache_hits}  ·  **Cache misses:** {manifest.cache_misses}",
        f"- **Reuse ratio:** {reuse_ratio:.0%}",
        f"- **Failures:** {manifest.failures}  ·  **Retries:** {manifest.retries}",
        f"- **Provider breakdown:** {breakdown_str}",
        f"- **Total cost:** ${total_cost:.4f}",
        f"- **Average generation time:** {avg:.2f}s",
        f"- **Total render time:** {manifest.duration_seconds:.2f}s",
        "",
        "## Per-shot",
        "",
        "| # | File | Shot | Scene | Provider | Model | Time (s) | Cost ($) | Resolution | "
        "Seed | Hash | Reuse key | Cache | Status |",
        "|---|------|------|-------|----------|-------|---------:|---------:|------------|"
        "-----:|------|-----------|:-----:|--------|",
    ]
    for i, a in enumerate(manifest.assets, start=1):
        provider = _winner(a)
        h = (a.get("image_hash") or a.get("hash") or "")[:12]
        cache = "yes" if a.get("cache", a.get("cached")) else "no"
        lines.append(
            f"| {i} | {a.get('filename','')} | {_md_cell(a.get('shot_id',''),24)} | "
            f"{_md_cell(a.get('scene') or a.get('scene_id',''),16)} | {provider} | "
            f"{_md_cell(a.get('model',''),34)} | "
            f"{float(a.get('generation_time',0.0)):.2f} | {float(a.get('cost',0.0)):.4f} | "
            f"{a.get('resolution','')} | {a.get('seed','')} | `{h}` | "
            f"{_md_cell(a.get('reuse_key',''),24) or '—'} | {cache} | {a.get('status','')} |"
        )

    # Prompts EXACTOS por plano (prompt + negative + reuse_key) — auditoría de fidelidad.
    lines += ["", "## Prompts (exact, as sent by VSC)", ""]
    for i, a in enumerate(manifest.assets, start=1):
        lines += [
            f"### {i}. {a.get('filename','')} — {a.get('shot_id','')} "
            f"({_winner(a)} / {a.get('model','')})",
            f"- **seed:** {a.get('seed','')}  ·  **reuse_key:** "
            f"{a.get('reuse_key','') or '—'}  ·  **resolution:** {a.get('resolution','')}",
            f"- **prompt:** {a.get('prompt','')}",
            f"- **negative_prompt:** {a.get('negative_prompt','') or '—'}",
            "",
        ]

    if manifest.failed:
        lines += ["## Failed shots", "",
                  "| Shot | Scene | Error |", "|------|-------|-------|"]
        for f in manifest.failed:
            lines.append(
                f"| {f.get('shot_id','')} | {f.get('scene_id','')} | {_md_cell(f.get('error',''),160)} |")

    return "\n".join(lines) + "\n"
