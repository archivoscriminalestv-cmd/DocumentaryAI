"""Modelos del Asset Library & Registry (ALR).

``Asset`` describe un recurso audiovisual PERMANENTE: identidad estable
(``asset_id`` direccionado por contenido), huellas (sha256/pHash/aHash), metadatos de
generación (proveedor, modelo, prompt, seed, identidad de personaje…) y la lista de
``references`` (dónde se ha usado: proyecto/escena/plano). Serializable y versionado.

El ``asset_id`` NUNCA depende del nombre de archivo ni del documental: deriva del
contenido (``asset_<sha256[:8]>``). Imágenes idénticas → mismo id → deduplicación.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.alr import SCHEMA_VERSION


def asset_id_for(sha256: str) -> str:
    """Id permanente y estable derivado del contenido."""
    return f"asset_{(sha256 or '')[:8]}"


@dataclass
class AssetReference:
    """Uso de un asset por un render concreto (un asset puede tener muchas)."""

    project: str = ""
    scene: str = ""
    shot: str = ""
    shot_id: str = ""
    render_id: str = ""
    created_at: str = ""

    def key(self) -> tuple:
        return (self.project, self.scene, self.shot, self.shot_id, self.render_id)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Asset:
    asset_id: str
    sha256: str
    schema_version: str = SCHEMA_VERSION
    # --- huellas perceptuales ---
    phash: str = ""
    ahash: str = ""
    # --- propiedades de imagen ---
    width: int = 0
    height: int = 0
    format: str = "PNG"
    size_bytes: int = 0
    # --- generación (intrínseco al asset) ---
    provider: str = ""
    model: str = ""
    prompt: str = ""
    negative_prompt: str = ""
    seed: int = 0
    reuse_key: str = ""
    character_identity: str = ""   # visual_identity_id (CCE)
    character_name: str = ""
    # --- contexto de origen (primer registro) ---
    project: str = ""
    scene: str = ""
    shot: str = ""
    shot_id: str = ""
    created_at: str = ""
    # --- biblioteca ---
    filename: str = ""             # relativo dentro de library/images
    # --- versionado / linaje ---
    parent_asset: str = ""
    possible_duplicates: list[str] = field(default_factory=list)
    # --- uso ---
    references: list[AssetReference] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    status: str = "active"         # active (nunca se borra)

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def reference_count(self) -> int:
        return len(self.references)

    def add_reference(self, ref: AssetReference) -> bool:
        """Añade una referencia si no existe ya. Devuelve True si era nueva."""
        if any(r.key() == ref.key() for r in self.references):
            return False
        self.references.append(ref)
        return True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["resolution"] = self.resolution
        data["reference_count"] = self.reference_count
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Asset":
        known = set(cls.__dataclass_fields__)
        kwargs = {k: v for k, v in data.items() if k in known}
        kwargs["references"] = [AssetReference(**r) for r in data.get("references", [])]
        return cls(**kwargs)
