"""Analiza una URL de YouTube con el YIE y guarda su conocimiento (YIE-001).

    python -m app.cli.inspect_youtube https://www.youtube.com/watch?v=XXXXXXXX

Genera en ``knowledge/documentaries/doc_yt_<id>/``:
    youtube.json · seo.json · thumbnail.json · popularity.json

No descarga el vídeo (solo metadatos + miniatura). No modifica el DLE ni la generación.
"""

import sys

from app.yie.orchestrator import YouTubeIntelligenceEngine


def run(url: str, *, engine: YouTubeIntelligenceEngine | None = None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    engine = engine or YouTubeIntelligenceEngine()
    result = engine.inspect(url)

    yt, seo, pop = result["youtube"], result["seo"], result["popularity"]
    print(f"Documental: {result['documentary_id']}  ·  datos: "
          f"{'sí' if result['available'] else 'no (UNKNOWN)'}")
    print(f"  título      : {yt.video.title}")
    print(f"  canal       : {yt.channel.channel_name}  ·  subs: {yt.channel.subscribers}")
    print(f"  vistas      : {yt.metrics.views}  ·  likes: {yt.metrics.likes}  ·  "
          f"comentarios: {yt.metrics.comments}")
    print(f"  SEO         : título {seo.title_length} car · {seo.title_word_count} palabras · "
          f"año={seo.has_year} pregunta={seo.is_question} emojis={seo.emoji_count}")
    print(f"  popularidad : edad {pop.age_days} d · views/día {pop.views_per_day} · "
          f"engagement {pop.engagement_rate}")
    print(f"  miniatura   : {result['thumbnail'].resolution} "
          f"(disponible={result['thumbnail'].available})")
    for name, path in result["paths"].items():
        print(f"  {name:10} -> {path}")
    return result


def main() -> None:
    if len(sys.argv) < 2:
        print("uso: python -m app.cli.inspect_youtube <URL de YouTube>")
        return
    run(sys.argv[1])


if __name__ == "__main__":
    main()
