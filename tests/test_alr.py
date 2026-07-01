"""Tests del Asset Library & Registry (ALR) — deterministas, sin red."""

import io

from PIL import Image

from app.alr import AssetLibrary, AssetRegistry, LibraryStorage, search_assets
from app.alr.deduplication import find_exact, find_perceptual
from app.alr.fingerprint import average_hash, hamming, perceptual_hash, sha256_bytes
from app.alr.models import Asset, AssetReference, asset_id_for


def _png(color=(20, 40, 60), size=(64, 36), noise=None) -> bytes:
    img = Image.new("RGB", size, color)
    if noise:
        img.putpixel((0, 0), noise)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _fixed_clock():
    return "2026-06-29T00:00:00+00:00"


def _meta(provider="huggingface", model="flux", prompt="a street", seed=7, char="Coquito"):
    return {"provider": provider, "model": model, "prompt": prompt, "negative_prompt": "blurry",
            "seed": seed, "reuse_key": "", "character_identity": "vid_x", "character_name": char}


def _ref(scene="scene-01", shot="shot-01", render="r1"):
    return AssetReference(project="coquito", scene=scene, shot=shot,
                          shot_id=f"{scene}::{shot}", render_id=render, created_at=_fixed_clock())


class _FakeManifest:
    def __init__(self, assets):
        self.assets = assets


# --- fingerprint -------------------------------------------------------------

def test_sha256_stable_and_content_addressed():
    data = _png()
    assert sha256_bytes(data) == sha256_bytes(data)
    assert asset_id_for(sha256_bytes(data)).startswith("asset_")


def test_phash_ahash_deterministic_and_similar_images_close():
    a = _png(color=(100, 100, 100))
    b = _png(color=(100, 100, 100), noise=(101, 100, 100))  # casi idéntica
    c = _png(color=(0, 0, 0))                               # muy distinta
    assert perceptual_hash(a) == perceptual_hash(a)         # determinista
    assert average_hash(a) == average_hash(a)
    assert hamming(perceptual_hash(a), perceptual_hash(b)) <= 6
    assert hamming(perceptual_hash(a), perceptual_hash(c)) >= 0  # comparable


# --- ingesta + id permanente -------------------------------------------------

def test_ingest_creates_permanent_asset(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    asset, status = lib.ingest_asset(_png(), _meta(), _ref())
    assert status == "new"
    assert asset.asset_id == asset_id_for(asset.sha256)
    assert asset.provider == "huggingface" and asset.character_name == "Coquito"
    assert asset.reference_count == 1
    # fichero físico escrito en library/images con nombre = asset_id
    assert (tmp_path / "library" / "images" / f"{asset.asset_id}.png").exists()
    assert (tmp_path / "library" / "metadata" / f"{asset.asset_id}.json").exists()


def test_identical_image_is_deduped_to_reference(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    a1, s1 = lib.ingest_asset(_png(), _meta(), _ref(render="r1"))
    a2, s2 = lib.ingest_asset(_png(), _meta(), _ref(render="r2"))  # mismo contenido, otro render
    assert s1 == "new" and s2 == "referenced"
    assert a1.asset_id == a2.asset_id                 # mismo id permanente
    assert len(lib.registry) == 1                     # NO se duplica el asset
    assert a2.reference_count == 2                    # pero crece la referencia
    # un único fichero físico
    images = list((tmp_path / "library" / "images").glob("*.png"))
    assert len(images) == 1


def test_same_reference_not_duplicated(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    lib.ingest_asset(_png(), _meta(), _ref(render="r1"))
    asset, _ = lib.ingest_asset(_png(), _meta(), _ref(render="r1"))  # misma referencia exacta
    assert asset.reference_count == 1


def test_perceptual_near_duplicate_flagged_not_deleted(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    a1, _ = lib.ingest_asset(_png(color=(100, 100, 100)), _meta(), _ref(shot="shot-01"))
    a2, status = lib.ingest_asset(_png(color=(100, 100, 100), noise=(101, 100, 100)),
                                  _meta(), _ref(shot="shot-02"))
    assert a1.asset_id != a2.asset_id                 # contenido distinto -> asset distinto
    assert status == "new_possible_duplicate"
    assert a1.asset_id in a2.possible_duplicates      # marcado, NO eliminado
    assert len(lib.registry) == 2


# --- persistencia: nunca se pierde nada --------------------------------------

def test_registry_persists_and_never_shrinks(tmp_path):
    root = str(tmp_path / "library")
    lib = AssetLibrary(root=root, now=_fixed_clock)
    lib.ingest_asset(_png(color=(1, 1, 1)), _meta(), _ref(shot="a"))
    lib.ingest_asset(_png(color=(2, 2, 2)), _meta(), _ref(shot="b"))
    lib.registry.save()
    # nueva instancia: carga lo persistido
    reloaded = AssetLibrary(root=root, now=_fixed_clock)
    assert len(reloaded.registry) == 2
    reloaded.ingest_asset(_png(color=(3, 3, 3)), _meta(), _ref(shot="c"))
    again = AssetLibrary(root=root, now=_fixed_clock)
    assert len(again.registry) == 3                   # solo crece


# --- ingest_render: render referencia, no posee ------------------------------

def _render_assets():
    return _FakeManifest([
        {"filename": "S01.png", "scene": "scene-01", "shot_id": "scene-01::shot-01",
         "provider": "huggingface", "model": "flux", "prompt": "p1", "negative_prompt": "n",
         "seed": 1, "reuse_key": "", "metadata": {"router_winner": "huggingface"}},
        {"filename": "S02.png", "scene": "scene-01", "shot_id": "scene-01::shot-02",
         "provider": "huggingface", "model": "flux", "prompt": "p2", "negative_prompt": "n",
         "seed": 1, "reuse_key": "", "metadata": {"router_winner": "huggingface"}},
    ])


def _write_render_dir(tmp_path):
    images = tmp_path / "render" / "images"
    images.mkdir(parents=True)
    (images / "S01.png").write_bytes(_png(color=(10, 20, 30)))
    (images / "S02.png").write_bytes(_png(color=(40, 50, 60)))
    return str(images)


def test_ingest_render_builds_reference_manifest(tmp_path):
    images_dir = _write_render_dir(tmp_path)
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    result = lib.ingest_render(_render_assets(), project="coquito", render_id="r1",
                               character_identity="vid_x", character_name="Coquito",
                               images_dir=images_dir)
    dm = result["manifest"].to_dict()
    assert dm["project"] == "coquito"
    assert len(dm["asset_ids"]) == 2
    assert all(aid.startswith("asset_") for aid in dm["asset_ids"])
    # el manifest referencia asset_id, nunca rutas de imagen del render
    shot = dm["scenes"]["scene-01"][0]
    assert "asset_id" in shot and shot["asset_id"].startswith("asset_")


def test_five_renders_only_grow_library(tmp_path):
    images_dir = _write_render_dir(tmp_path)
    root = str(tmp_path / "library")
    sizes, reuses = [], []
    for i in range(5):
        lib = AssetLibrary(root=root, now=_fixed_clock)
        lib.ingest_render(_render_assets(), project="coquito", render_id=f"r{i}",
                          character_identity="vid_x", character_name="Coquito",
                          images_dir=images_dir)
        sizes.append(len(lib.registry))
        reuses.append(lib.stats()["total_references"])
    # mismas imágenes -> assets NO crecen (dedup), pero las referencias SÍ
    assert sizes == [2, 2, 2, 2, 2]
    assert reuses == [2, 4, 6, 8, 10]
    # ninguna imagen se borró: 2 ficheros físicos siguen ahí
    assert len(list((tmp_path / "library" / "images").glob("*.png"))) == 2


# --- búsqueda ----------------------------------------------------------------

def test_search_by_fields(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    lib.ingest_asset(_png(color=(1, 2, 3)), _meta(provider="huggingface", char="Coquito"),
                     _ref(scene="scene-01"))
    lib.ingest_asset(_png(color=(4, 5, 6)), _meta(provider="openai", char="Tesla"),
                     _ref(scene="scene-02"))
    assert len(search_assets(lib.registry, provider="huggingface")) == 1
    assert len(search_assets(lib.registry, character="Coquito")) == 1
    assert len(search_assets(lib.registry, scene="scene-02")) == 1
    assert len(search_assets(lib.registry, identity="vid_x")) == 2
    assert search_assets(lib.registry, provider="huggingface", scene="scene-02") == []


# --- serialización + versionado ----------------------------------------------

def test_asset_roundtrip_serialization(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    asset, _ = lib.ingest_asset(_png(), _meta(), _ref())
    restored = Asset.from_dict(asset.to_dict())
    assert restored.to_dict() == asset.to_dict()
    assert restored.schema_version == asset.schema_version
    assert restored.references[0].render_id == "r1"


def test_versioning_via_parent_asset(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    v1, _ = lib.ingest_asset(_png(color=(10, 10, 10)), _meta(), _ref())
    v2, _ = lib.ingest_asset(_png(color=(11, 11, 11)), _meta(), _ref())
    v2.parent_asset = v1.asset_id                     # mejora enlazada, sin sobreescribir
    assert v1.asset_id in lib.registry and v2.asset_id in lib.registry
    assert v2.parent_asset == v1.asset_id


# --- informe -----------------------------------------------------------------

def test_report_contains_stats(tmp_path):
    lib = AssetLibrary(root=str(tmp_path / "library"), now=_fixed_clock)
    lib.ingest_asset(_png(color=(1, 1, 1)), _meta(), _ref(render="r1"))
    lib.ingest_asset(_png(color=(1, 1, 1)), _meta(), _ref(render="r2"))  # reuse
    report = lib.report()
    assert "Total assets (permanent):** 1" in report
    assert "Total references" in report and "huggingface" in report
    assert "Reuse ratio" in report
