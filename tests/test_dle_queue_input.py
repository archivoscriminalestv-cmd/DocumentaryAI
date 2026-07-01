"""Tests del parser de entradas y los prerequisitos del Downloader (DLE-002B).

Deterministas y sin red. Cubren: URL suelta, fichero TXT, directorio con varios TXT,
comentarios, líneas vacías, URLs inválidas, duplicados (lote/cola/aprendidas),
estadísticas y el informe de entorno con herramientas ausentes.
"""

import os

from app.dle.queue import LearningQueueManager
from app.dle.queue.environment import check_downloader_environment
from app.dle.queue.index import KnowledgeIndex
from app.dle.queue.input_parser import QueueInputParser, is_valid_url
from app.dle.queue.store import QueueStore


YT = "https://youtu.be/vid{:05d}aaa"


# --- validación de URLs ------------------------------------------------------
def test_is_valid_url():
    assert is_valid_url("https://youtu.be/abc123")
    assert is_valid_url("http://example.com/x")
    assert not is_valid_url("not-a-url")
    assert not is_valid_url("ftp://x")
    assert not is_valid_url("")
    assert not is_valid_url("datasets/youtube/urls.txt")


# --- caso 1: URL individual --------------------------------------------------
def test_single_url():
    result = QueueInputParser().parse(["https://youtu.be/abcdef"])
    assert result.added == ["https://youtu.be/abcdef"]
    assert result.found == 1 and result.duplicates == 0 and result.invalid == []
    assert result.sources_read == []   # no se leyó ningún fichero


# --- caso 2: fichero TXT (comentarios, vacías, inválidas, duplicados) --------
def test_txt_file_parsing(tmp_path):
    txt = tmp_path / "urls.txt"
    txt.write_text(
        "\n".join([
            "# lista de documentales",
            "https://youtu.be/aaaaaa",
            "",
            "   https://youtu.be/bbbbbb   ",   # espacios
            "# otro comentario",
            "https://youtu.be/aaaaaa",          # duplicado en el lote
            "esto-no-es-url",                   # inválida
        ]),
        encoding="utf-8",
    )
    result = QueueInputParser().parse([str(txt)])
    assert result.added == ["https://youtu.be/aaaaaa", "https://youtu.be/bbbbbb"]
    assert result.duplicates == 1
    assert result.invalid == ["esto-no-es-url"]
    assert result.found == 4          # 2 válidas + 1 duplicada + 1 inválida
    assert result.sources_read == [str(txt)]
    # NUNCA se encola el propio .txt
    assert str(txt) not in result.added


# --- caso 3: directorio con varios TXT ---------------------------------------
def test_directory_with_multiple_txt(tmp_path):
    (tmp_path / "a.txt").write_text("https://youtu.be/aaaaaa\n# c\nhttps://youtu.be/bbbbbb\n",
                                    encoding="utf-8")
    (tmp_path / "b.txt").write_text("https://youtu.be/cccccc\nhttps://youtu.be/aaaaaa\n",
                                    encoding="utf-8")
    (tmp_path / "notes.md").write_text("https://youtu.be/ignored\n", encoding="utf-8")  # no .txt
    result = QueueInputParser().parse([str(tmp_path)])
    assert result.added == ["https://youtu.be/aaaaaa", "https://youtu.be/bbbbbb",
                            "https://youtu.be/cccccc"]
    assert result.duplicates == 1                      # aaaaaa repetida en b.txt
    assert len(result.sources_read) == 2               # solo los .txt
    assert all(s.endswith(".txt") for s in result.sources_read)


# --- duplicados contra cola y conocimiento -----------------------------------
def test_dedup_against_queue_and_learned():
    parser = QueueInputParser(
        existing=lambda u: u == "https://youtu.be/inqueue00",
        learned=lambda u: u == "https://youtu.be/learned000",
    )
    result = parser.parse([
        "https://youtu.be/new0000000",
        "https://youtu.be/inqueue00",     # ya en cola
        "https://youtu.be/learned000",    # ya aprendida
    ])
    assert result.added == ["https://youtu.be/new0000000"]
    assert result.duplicates == 2


# --- estadísticas del parser -------------------------------------------------
def test_parser_statistics(tmp_path):
    txt = tmp_path / "u.txt"
    lines = [YT.format(i) for i in range(120)]
    lines += [YT.format(0), YT.format(1)]      # 2 duplicadas
    lines += ["bad-1", "bad-2", "bad-3"]       # 3 inválidas
    txt.write_text("\n".join(lines), encoding="utf-8")
    result = QueueInputParser().parse([str(txt)])
    assert result.found == 125
    assert result.valid == 120
    assert result.duplicates == 2
    assert len(result.invalid) == 3


# --- nunca encola un .txt como QueueItem -------------------------------------
def test_txt_never_becomes_queue_item(tmp_path):
    txt = tmp_path / "truecrime_urls.txt"
    txt.write_text("https://youtu.be/realdoc001\n", encoding="utf-8")
    mgr = LearningQueueManager(
        store=QueueStore(str(tmp_path / "q.json")),
        index=KnowledgeIndex(str(tmp_path / "idx.json")),
        knowledge_root=str(tmp_path / "knowledge"),
    )
    from app.cli.queue_add import run
    run([str(txt)], manager=mgr, show_environment=False)
    urls = [i.url for i in mgr.store.ordered()]
    assert urls == ["https://youtu.be/realdoc001"]
    assert not any(u.endswith(".txt") for u in urls)


# --- CLI end-to-end con cola real --------------------------------------------
def test_cli_run_adds_and_dedups(tmp_path):
    txt = tmp_path / "urls.txt"
    txt.write_text("\n".join([YT.format(i) for i in range(5)] + [YT.format(0)]),
                   encoding="utf-8")
    mgr = LearningQueueManager(
        store=QueueStore(str(tmp_path / "q.json")),
        index=KnowledgeIndex(str(tmp_path / "idx.json")),
        knowledge_root=str(tmp_path / "knowledge"),
    )
    from app.cli.queue_add import run
    out = run([str(txt)], manager=mgr, show_environment=False)
    assert out == {"found": 6, "added": 5, "duplicates": 1, "invalid": 0}
    # segunda ejecución: todo ya en cola -> 0 añadidas
    out2 = run([str(txt)], manager=mgr, show_environment=False)
    assert out2["added"] == 0 and out2["duplicates"] == 6


# --- entorno: herramientas ausentes ------------------------------------------
def test_environment_all_available():
    report = check_downloader_environment(
        ytdlp=lambda: (True, "/bin/yt-dlp"),
        ffmpeg=lambda: (True, "/bin/ffmpeg"),
        whisper=lambda: (True, "whisper"),
    )
    assert report.ready() is True
    assert "yt-dlp" in report.format() and "OK" in report.format()


def test_environment_without_ytdlp():
    report = check_downloader_environment(
        ytdlp=lambda: (False, ""),
        ffmpeg=lambda: (True, "/bin/ffmpeg"),
        whisper=lambda: (True, "whisper"),
    )
    assert report.get("yt-dlp").available is False
    assert report.ready() is False          # yt-dlp no es opcional
    assert "unavailable" in report.format()


def test_environment_without_ffmpeg():
    report = check_downloader_environment(
        ytdlp=lambda: (True, "/bin/yt-dlp"),
        ffmpeg=lambda: (False, ""),
        whisper=lambda: (True, "whisper"),
    )
    assert report.get("ffmpeg").available is False
    assert report.ready() is False


def test_environment_without_whisper_is_optional():
    report = check_downloader_environment(
        ytdlp=lambda: (True, "/bin/yt-dlp"),
        ffmpeg=lambda: (True, "/bin/ffmpeg"),
        whisper=lambda: (False, ""),
    )
    assert report.get("Whisper").available is False
    assert report.get("Whisper").optional is True
    assert report.ready() is True           # Whisper es opcional


def test_environment_detects_module_only_ytdlp(monkeypatch):
    """Si yt-dlp no está en PATH pero el módulo yt_dlp sí, se reporta disponible."""
    import app.dle.queue.environment as e
    monkeypatch.setattr(e.shutil, "which", lambda name: None)
    monkeypatch.setattr(e.importlib.util, "find_spec", lambda name: object())
    ok, detail = e._detect_ytdlp()
    assert ok is True and "yt_dlp" in detail


def test_environment_detector_never_raises():
    def boom():
        raise RuntimeError("kaboom")

    report = check_downloader_environment(ytdlp=boom, ffmpeg=boom, whisper=boom)
    assert report.get("yt-dlp").available is False   # no propaga la excepción
    assert "error" in report.get("yt-dlp").detail


# --- regresión bug DLE-002B: URLs reales de YouTube --------------------------
REAL_YT = [
    "https://www.youtube.com/watch?v=F0tfsMwKk-M",
    "https://www.youtube.com/watch?v=fHho90TtqlA",
    "https://www.youtube.com/watch?v=Lup5gpaX5WY",
    "https://www.youtube.com/watch?v=fDeDmgkXaNg",
    "https://www.youtube.com/watch?v=9SNqC23y1Z4",
]


def test_real_youtube_urls_are_valid():
    for url in REAL_YT:
        assert is_valid_url(url), url
    assert is_valid_url("https://youtu.be/F0tfsMwKk-M")


def test_real_youtube_file_crlf_returns_five(tmp_path):
    # fichero como el real: 5 líneas, finales CRLF, sin newline final
    txt = tmp_path / "truecrime_urls.txt"
    txt.write_bytes(("\r\n".join(REAL_YT)).encode("utf-8"))
    result = QueueInputParser().parse([str(txt)])
    assert result.found == 5
    assert result.valid == 5
    assert result.added == REAL_YT
    assert result.invalid == [] and result.duplicates == 0


def test_file_with_utf8_bom_is_handled(tmp_path):
    txt = tmp_path / "bom.txt"
    txt.write_bytes(("\r\n".join(REAL_YT)).encode("utf-8-sig"))  # con BOM
    result = QueueInputParser().parse([str(txt)])
    assert result.valid == 5 and result.invalid == []


def test_is_valid_url_tolerates_bom_prefix():
    assert is_valid_url("﻿https://www.youtube.com/watch?v=F0tfsMwKk-M")


def test_missing_path_is_reported_not_counted_as_invalid_url(tmp_path):
    # raíz del bug: la ruta tecleada no existe (p.ej. doble extensión .txt.txt)
    missing = str(tmp_path / "truecrime_urls.txt")
    result = QueueInputParser().parse([missing])
    assert result.missing == [missing]
    assert result.found == 0 and result.valid == 0 and result.invalid == []


def test_double_extension_scenario(tmp_path):
    real = tmp_path / "truecrime_urls.txt.txt"        # fichero real en disco
    real.write_bytes(("\r\n".join(REAL_YT)).encode("utf-8"))
    typed = tmp_path / "truecrime_urls.txt"           # lo que el usuario teclea (no existe)

    assert QueueInputParser().parse([str(real)]).valid == 5     # el real funciona
    typed_result = QueueInputParser().parse([str(typed)])
    assert typed_result.valid == 0 and typed_result.missing == [str(typed)]
