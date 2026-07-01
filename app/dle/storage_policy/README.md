# DLE Storage Policy — Temporary Video Lifecycle (DLE-002A)

El vídeo descargado durante el aprendizaje es un **recurso temporal**: un medio para
obtener conocimiento, no parte de la base de datos. La **fuente de verdad** es el
conocimiento (URL + metadatos + análisis + estadísticas + embeddings + informes), nunca el
fichero de vídeo — salvo que se solicite archivarlo explícitamente.

Subsistema **desacoplado**: el Downloader nunca decide qué hacer con el fichero; lo decide
la **política de almacenamiento**.

```
URL → descargar en workspace temporal → analizar → guardar conocimiento → (política) borrar/archivar
```

## Modos (`LEARNING_STORAGE_MODE`)

| Modo | Comportamiento |
|------|----------------|
| **TEMPORARY** (por defecto) | descarga → analiza → guarda conocimiento → **elimina el vídeo** automáticamente |
| **ARCHIVE** | igual, pero **conserva el vídeo** en `archive/videos/` (solo para referencia) |
| **STREAM** | interfaz reservada, **sin implementación** todavía (lanza `NotImplementedError`) |

## Módulos (`app/dle/storage_policy/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `base.py` | `BaseStoragePolicy` (workspace context-manager) + salvaguardas de borrado (`safe_rmtree`, `is_protected`) |
| `temporary.py` | `TemporaryStoragePolicy` — borra el workspace al finalizar (éxito **o** error) |
| `archive.py` | `ArchiveStoragePolicy` — mueve el vídeo a `archive/videos/` y limpia el resto |
| `storage_policy.py` | `build_storage_policy()` (factory por env) + `StreamStoragePolicy` (stub) |

## Garantías

- **Sin residuos:** el workspace temporal (`cache/learning/<key>/`) se elimina al terminar,
  también si el análisis falla. Los vídeos temporales nunca se guardan en `knowledge/`.
- **Seguridad dura:** `safe_rmtree` solo borra dentro de la raíz temporal de la política y
  **se niega** a tocar `knowledge/`, `library/`, `output/`, `assets/`.
- **Conocimiento independiente del vídeo:** el conocimiento se guarda **antes** de finalizar
  el workspace; se puede reconstruir solo con los JSON de `knowledge/`.
- **Desacoplado y aditivo:** se inyecta en el motor (`DocumentaryLearningEngine(storage_policy=…)`,
  por defecto TEMPORARY leyendo `LEARNING_STORAGE_MODE`). No cambia el análisis, la cola, el
  Knowledge Store ni el formato de conocimiento.

## Decisión arquitectónica

Ver `docs/adr/ADR-0010-Temporary-Assets-vs-Permanent-Knowledge.md`.
