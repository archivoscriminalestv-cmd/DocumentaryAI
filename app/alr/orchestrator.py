"""AssetLibrary — fachada del ALR (ingesta, deduplicación, registro, informes).

Se invoca DESPUÉS del VPL: dada la salida del render (imágenes ya generadas en el
directorio temporal), registra cada asset en la biblioteca PERMANENTE, deduplica por
contenido y devuelve los ``asset_id`` + rutas permanentes y un manifest por referencia.

Nunca borra, nunca sobreescribe binarios existentes. El render solo referencia.
"""

import logging
import os
from datetime import datetime, timezone

from app.alr.deduplication import DEFAULT_PHASH_THRESHOLD, find_exact, find_perceptual
from app.alr.fingerprint import (
    average_hash,
    image_properties,
    perceptual_hash,
    sha256_bytes,
)
from app.alr.manifest import DocumentaryManifest, ShotReference
from app.alr.models import Asset, AssetReference, asset_id_for
from app.alr.registry import AssetRegistry
from app.alr.storage import LibraryStorage


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _shot_label(shot_id: str) -> str:
    return shot_id.split("::")[-1] if shot_id else ""


class AssetLibrary:
    def __init__(self, root: str = "library", *, logger=None, now=_now,
                 phash_threshold: int = DEFAULT_PHASH_THRESHOLD) -> None:
        self.storage = LibraryStorage(root)
        self.registry = AssetRegistry(self.storage).load()
        self._log = logger or logging.getLogger("alr")
        self._now = now
        self._threshold = phash_threshold

    # ------------------------------------------------------------------ ingesta

    def ingest_asset(self, data: bytes, meta: dict, reference: AssetReference) -> tuple[Asset, str]:
        """Registra una imagen. Devuelve (asset, status).

        status: ``referenced`` (ya existía, solo nueva referencia) | ``new`` |
        ``new_possible_duplicate`` (nuevo pero perceptualmente cercano a otro).
        """
        sha = sha256_bytes(data)

        existing = find_exact(self.registry, sha)
        if existing is not None:
            existing.add_reference(reference)
            self.storage.write_metadata(existing.asset_id, existing.to_dict())
            self.registry.save()
            return existing, "referenced"

        asset_id = asset_id_for(sha)
        phash = perceptual_hash(data)
        ahash = average_hash(data)
        width, height, fmt = image_properties(data)
        dups = find_perceptual(self.registry, phash, threshold=self._threshold, exclude_sha=sha)
        filename = self.storage.write_image(asset_id, fmt, data)

        asset = Asset(
            asset_id=asset_id, sha256=sha, phash=phash, ahash=ahash,
            width=width, height=height, format=fmt, size_bytes=len(data),
            provider=str(meta.get("provider", "")), model=str(meta.get("model", "")),
            prompt=str(meta.get("prompt", "")), negative_prompt=str(meta.get("negative_prompt", "")),
            seed=int(meta.get("seed", 0) or 0), reuse_key=str(meta.get("reuse_key", "")),
            character_identity=str(meta.get("character_identity", "")),
            character_name=str(meta.get("character_name", "")),
            project=reference.project, scene=reference.scene, shot=reference.shot,
            shot_id=reference.shot_id, created_at=reference.created_at,
            filename=filename, possible_duplicates=dups,
            references=[reference], tags=list(meta.get("tags", []) or []),
        )
        self.registry.add(asset)
        self.storage.write_metadata(asset_id, asset.to_dict())
        self.registry.save()
        return asset, ("new_possible_duplicate" if dups else "new")

    def ingest_render(self, vpl_manifest, *, project: str, render_id: str = "",
                      character_identity: str = "", character_name: str = "",
                      images_dir: str) -> dict:
        """Ingiere todos los assets de un render del VPL y devuelve el resumen."""
        render_id = render_id or self._now()
        dm = DocumentaryManifest(project=project, render_id=render_id)
        summary = {"new": 0, "referenced": 0, "new_possible_duplicate": 0, "skipped": 0}

        for a in getattr(vpl_manifest, "assets", []) or []:
            filename = a.get("filename", "")
            path = os.path.join(images_dir, filename)
            if not filename or not os.path.exists(path):
                summary["skipped"] += 1
                continue
            with open(path, "rb") as handle:
                data = handle.read()

            scene = a.get("scene") or a.get("scene_id") or ""
            shot_id = a.get("shot_id", "")
            ref = AssetReference(project=project, scene=scene, shot=_shot_label(shot_id),
                                 shot_id=shot_id, render_id=render_id, created_at=self._now())
            meta = {
                "provider": a.get("metadata", {}).get("router_winner") or a.get("provider", ""),
                "model": a.get("model", ""), "prompt": a.get("prompt", ""),
                "negative_prompt": a.get("negative_prompt", ""), "seed": a.get("seed", 0),
                "reuse_key": a.get("reuse_key", ""),
                "character_identity": character_identity, "character_name": character_name,
            }
            asset, status = self.ingest_asset(data, meta, ref)
            summary[status] = summary.get(status, 0) + 1
            dm.add(scene, ShotReference(
                shot=_shot_label(shot_id), shot_id=shot_id, asset_id=asset.asset_id,
                library_path=self.storage.image_path(asset.asset_id, asset.format),
                status=status,
            ))

        self.registry.save()
        return {"manifest": dm, "summary": summary,
                "library_size": len(self.registry), "render_id": render_id}

    # ------------------------------------------------------------------ informe

    def stats(self) -> dict:
        assets = self.registry.all()
        total_refs = sum(a.reference_count for a in assets)
        by_provider, by_model, by_character, by_project = {}, {}, {}, {}
        size = 0
        reused = 0
        dups = 0
        for a in assets:
            size += a.size_bytes
            by_provider[a.provider or "?"] = by_provider.get(a.provider or "?", 0) + 1
            by_model[a.model or "?"] = by_model.get(a.model or "?", 0) + 1
            name = a.character_name or "(none)"
            by_character[name] = by_character.get(name, 0) + 1
            if a.reference_count > 1:
                reused += 1
            if a.possible_duplicates:
                dups += 1
            for ref in a.references:
                p = ref.project or "?"
                by_project[p] = by_project.get(p, 0) + 1
        reuse_ratio = round(1 - (len(assets) / total_refs), 3) if total_refs else 0.0
        return {
            "total_assets": len(assets), "total_references": total_refs,
            "reused_assets": reused, "possible_duplicates": dups,
            "reuse_ratio": reuse_ratio, "size_bytes": size,
            "by_provider": by_provider, "by_model": by_model,
            "by_character": by_character, "by_project": by_project,
        }

    def report(self) -> str:
        s = self.stats()
        mb = s["size_bytes"] / (1024 * 1024)

        def _table(title: str, mapping: dict) -> list[str]:
            rows = [f"- **{k}:** {v}" for k, v in sorted(mapping.items(), key=lambda kv: -kv[1])]
            return [f"### {title}", "", *(rows or ["- (none)"]), ""]

        lines = [
            "# Asset Library report",
            "",
            f"- **Total assets (permanent):** {s['total_assets']}",
            f"- **Total references (uses across renders):** {s['total_references']}",
            f"- **Reused assets (referenced >1):** {s['reused_assets']}",
            f"- **Reuse ratio:** {s['reuse_ratio']:.0%}",
            f"- **Possible perceptual duplicates:** {s['possible_duplicates']}",
            f"- **Disk space:** {mb:.2f} MB ({s['size_bytes']} bytes)",
            "",
            *_table("Assets by provider", s["by_provider"]),
            *_table("Assets by model", s["by_model"]),
            *_table("Assets by character", s["by_character"]),
            *_table("References by project", s["by_project"]),
        ]
        return "\n".join(lines)

    def write_report(self, path: str = "") -> str:
        path = path or os.path.join(self.storage.root, "library_report.md")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.report())
        return path
