# ALR — Asset Library & Registry

Fuente **oficial de verdad** de todos los recursos audiovisuales generados por
DocumentaryAI. Filosofía: **cada asset es permanente** — nunca se elimina, nunca se
sobreescribe, nunca cambia de id, aunque se rendericen cien veces los mismos
documentales. El render solo **referencia** assets; nunca los reemplaza.

Subsistema **aditivo** e independiente. No modifica CRE/CCE/ERE/VIS/VAI/VSC/VPL/
Composer/Motion/FFmpeg. Se integra **después** del VPL: registra cada imagen ya
generada y devuelve un `asset_id` estable + su ruta permanente.

```
VPL (genera) → output/documentary/images/  (TEMPORAL, sobrescribible)
                        │
                        ▼
                 AssetLibrary.ingest_render()
                        │   sha256 + pHash + aHash, dedup, registro
                        ▼
library/
  images/    asset_<sha8>.png      (PERMANENTE, direccionado por contenido)
  metadata/  asset_<sha8>.json
  asset_registry.json              (índice de todos los assets)

documentary_manifest.json: project → scene → shot → asset_id   (solo REFERENCIAS)
```

## Módulos (`app/alr/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `Asset` (permanente), `AssetReference` (uso por render); `asset_id_for(sha)` |
| `fingerprint.py` | SHA256 + Average Hash + Perceptual Hash (DCT en Python puro) + Hamming |
| `storage.py` | `LibraryStorage`: escribe imágenes/metadata; **nunca** sobreescribe ni borra |
| `registry.py` | `AssetRegistry`: índice cargable/guardable (`asset_registry.json`) |
| `deduplication.py` | exacta (SHA256) + perceptual (pHash ≤ umbral → `possible_duplicate`) |
| `search.py` | `search_assets()` por provider/model/prompt/character/identity/project/scene/shot/tags/fecha |
| `manifest.py` | `DocumentaryManifest`: documental por referencia (asset_id, no imágenes) |
| `orchestrator.py` | `AssetLibrary`: ingesta de render, estadísticas, `library_report.md` |

## Asset ID permanente

`asset_id = asset_<primeros 8 hex del SHA256 del contenido>` (p.ej. `asset_9f8c2e71`).
Estable, **direccionado por contenido**: imágenes idénticas → mismo id → deduplicación
automática. No depende del nombre de archivo ni del documental ni del render. El nombre
del fichero físico **es** el `asset_id` (`library/images/asset_9f8c2e71.png`).

## Deduplicación

- **Exacta** (mismo SHA256): no se copia; solo se añade una `AssetReference` nueva.
- **Perceptual** (pHash con Hamming ≤ `DEFAULT_PHASH_THRESHOLD`): se registra como asset
  nuevo y se **marca** `possible_duplicates`, pero **nunca** se elimina ni se fusiona.

## Versionado

Una mejora de una imagen es un asset nuevo (otro contenido → otro id) enlazado por
`parent_asset`. Existe historial; no se sobreescribe nada.

## Búsqueda

```bash
python -m app.cli.library_report
python -m app.cli.library_report --search character=Coquito provider=huggingface scene=scene-02
```

Filtros combinables (AND): `asset_id`, `provider`, `model`, `prompt` (subcadena),
`character`, `identity`, `project`, `scene`, `shot`, `tag`, `date` (los de contexto
miran también las `references`).

## Estadísticas (`library_report.md`)

Total de assets, total de referencias (usos a lo largo de renders), assets reutilizados,
ratio de reutilización, posibles duplicados, espacio en disco, y desglose por proveedor,
modelo, personaje y proyecto.

## Decisiones arquitectónicas

Ver `docs/adr/ADR-0004-Assets-Are-Permanent-Content-Addressed.md`.

- **Permanencia y direccionamiento por contenido.** El id deriva del SHA256 → dedup
  natural, estabilidad eterna, independencia del render.
- **El render referencia, no posee.** `documentary_manifest` mapea escena/plano →
  `asset_id`; `output/documentary/images` pasa a ser un directorio temporal.
- **Integración aditiva tras el VPL.** El VPL no cambia; el CLI llama a `AssetLibrary`
  después del render para ingerir y referenciar.
- **Durabilidad por ingesta.** Cada `ingest_asset` persiste registro + metadata: si el
  proceso muere a mitad, los assets ya ingeridos siguen existiendo.

## Criterio de éxito (demostrado)

Ejecutar `python -m app.cli.generate_documentary` 5 veces: el render 1 crea N assets
permanentes; los renders 2–5 añaden **0 assets nuevos** (mismas imágenes → dedup) y
**solo referencias**. La biblioteca nunca encoge, nada se borra y la reutilización
crece con el tiempo.
