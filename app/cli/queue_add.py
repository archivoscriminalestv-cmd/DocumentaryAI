"""Añade entradas a la cola de aprendizaje (DLE-002 · parser DLE-002B).

    python -m app.cli.queue_add https://youtu.be/xxxx           # una URL
    python -m app.cli.queue_add datasets/youtube/urls.txt        # un fichero .txt de URLs
    python -m app.cli.queue_add datasets/youtube/                # un directorio (todos los *.txt)

Lee ficheros/directorios, ignora líneas vacías y comentarios (#), valida y deduplica
las URLs (contra el lote, la cola y lo ya aprendido) y crea un QueueItem por cada
documental. Nunca encola el propio fichero .txt. Muestra el estado del entorno
(yt-dlp / ffmpeg / Whisper) antes de empezar.
"""

import sys

from app.dle.queue import LearningQueueManager
from app.dle.queue.environment import check_downloader_environment
from app.dle.queue.input_parser import QueueInputParser


def run(args: list[str], *, manager: LearningQueueManager | None = None,
        parser: QueueInputParser | None = None, show_environment: bool = True) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    mgr = manager or LearningQueueManager()

    if show_environment:
        print(check_downloader_environment().format())
        print()

    parser = parser or QueueInputParser(
        existing=lambda url: mgr.store.get(url) is not None,
        learned=lambda url: mgr.index.find(url=url) is not None,
    )
    result = parser.parse(args)

    if result.sources_read:
        print("Leyendo:")
        for source in result.sources_read:
            print(f"  {source}")
        print()

    if result.missing:
        print("No reconocido (ni URL válida ni fichero/directorio existente):")
        for item in result.missing:
            print(f"  {item}")
        print("  (revisa la ruta y la extensión real del fichero, p.ej. '.txt.txt')")
        print()

    print(f"URLs encontradas ........ {result.found}")
    print(f"Válidas ................. {result.valid}")
    print(f"Duplicadas .............. {result.duplicates}")
    print(f"Inválidas ............... {len(result.invalid)}")
    print()

    added = mgr.add_urls(result.added)
    print(f"Añadidas a la cola ...... {added}")
    return {"found": result.found, "added": added, "duplicates": result.duplicates,
            "invalid": len(result.invalid)}


def main() -> None:
    if len(sys.argv) < 2:
        print("uso: python -m app.cli.queue_add <URL | fichero.txt | directorio> [...]")
        return
    run(sys.argv[1:])


if __name__ == "__main__":
    main()
