# VPL — Visual Provider Layer

La **frontera de ejecución** permanente entre la planificación cinematográfica de
DocumentaryAI (VIS/VAI/VSC) y cualquier tecnología de generación de imágenes.
Consume `VisualGenerationRequest` (del VSC) y produce `GeneratedAsset` reales.

```
VIS → VAI → VSC → VisualGenerationRequest
                        │
                        ▼
        VisualGenerationOrchestrator   (cola → workers → provider)
          ├─ AssetCache (reuse)        ├─ retry (backoff)   ├─ progress/logging
          ▼
        VisualProvider (adapter)  →  GeneratedAsset  →  images/ + metadata/ + manifest.json
```

Ningún componente fuera del VPL sabe qué proveedor generó una imagen. Toda la
lógica provider-specific vive **solo** en `adapters/`.

## Módulos (`app/vpl/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `GeneratedAsset` (serializable; `image_bytes` transitorio), `GenerationManifest`, `GenerationFailure` |
| `provider.py` | `VisualProvider` (Protocol) + `ProviderError(transient=…)` |
| `config.py` | `VPLConfig.from_env()` + `build_provider()` (selección por `VISUAL_PROVIDER`) |
| `cache.py` | `AssetCache` en disco; clave de dos vías (reuse_key / contenido), incluye provider+model |
| `retry.py` | `run_with_retry` (backoff exponencial; solo errores transitorios; `sleep` inyectable) |
| `queue.py` | `WorkerPool` (concurrencia con orden preservado) |
| `progress.py` | `Progress` (contadores thread-safe + logging estructurado) |
| `orchestrator.py` | `VisualGenerationOrchestrator` — coordina todo; lock por clave (anti-duplicado) |
| `adapters/` | `mock`, `openai` (real), `google_imagen` (estructura), `flux` (estructura) |

## Proveedores (VPL-002: reales)

Adapters reales con HTTP inyectable (tests sin red en `app/vpl/http.py`). Ejecutan
EXACTAMENTE el prompt/negativos compilados por el VSC (sin reinterpretar el estilo).

- **mock** — siempre disponible, PNG determinista. Tests y demo offline. Nunca se elimina.
- **openai** — Images API (`gpt-image-1`), `OPENAI_API_KEY`. Negativos como cláusula
  "Avoid:" (la API no tiene negative nativo). Tamaño mapeado a los soportados.
- **imagen** — Generative Language API (`imagen-3.0-generate-002`), `GOOGLE_API_KEY`.
  `negativePrompt` y `aspectRatio` NATIVOS.
- **flux** — Black Forest Labs (submit→poll→download), `FLUX_API_KEY`; base URL
  configurable (`FLUX_API_URL`) para self-hosted.

Detección de configuración: `is_available()` por adapter + `available_providers()`.
Si falta la clave, el adapter lanza `ProviderError` permanente → el orquestador lo
registra como fallo y CONTINÚA (no bloquea); se puede cambiar de proveedor solo por
`VISUAL_PROVIDER`. Telemetría final en `telemetry.build_report(manifest)`.

## Orquestación, capacidades y benchmark (VPL-003)

- **Capacidades** (`models.ProviderCapabilities`): cada adapter declara
  `capabilities()` (coste, negative nativo, seed nativo, resolución máx, formatos,
  submit→poll, self-hostable, env var, disponibilidad runtime). Registro:
  `config.provider_capabilities()`.
- **Fallback automático** (`strategy.ProviderChain`): orden de prioridad
  Primary → Secondary → Tertiary → **Mock**. Si un eslabón falla o no está
  configurado, pasa al siguiente; mock (siempre disponible) es la red de seguridad
  final, así el pipeline nunca queda sin imagen. La cadena implementa
  `VisualProvider`, así que el orquestador la usa sin cambios; anota en el asset
  `chain_winner`/`chain_attempted`/`chain_fallback`. Activación SOLO por config:
  ```
  VPL_FALLBACK=1                       # cadena = [VISUAL_PROVIDER, mock]
  VPL_PROVIDER_CHAIN=openai,imagen,flux,mock   # orden explícito (mock se garantiza)
  ```
- **Benchmark** (`benchmark.BenchmarkRunner` + CLI): genera el MISMO request con
  varios proveedores y compara coste/tiempo/modelo/metadatos.
  ```
  python -m app.cli.benchmark_shot
  BENCHMARK_PROVIDERS=openai,imagen,mock  BENCHMARK_SHOT_INDEX=5  python -m app.cli.benchmark_shot
  ```
  Salida en `output/benchmark/`: una imagen por proveedor con éxito + `benchmark.json`
  (incluye `cheapest`/`fastest`). Proveedores sin clave → `available=False`, no bloquean.

## Configuración (cambio de proveedor SIN tocar código)

```
VISUAL_PROVIDER=mock|openai|imagen|flux
VISUAL_MODEL=...        VPL_WORKERS=4       VPL_MAX_RETRIES=2
VPL_BASE_DELAY=0.5      VPL_CACHE_DIR=output/.vpl_cache
VPL_FALLBACK=0|1        VPL_PROVIDER_CHAIN=openai,imagen,flux,mock
```

## Caché

Clave incluye reuse_key, provider, model, seed y hash del prompt. Dos vías:
- `reuse_key` no vacío → estable por localización/asset (reutiliza entre escenas),
- `reuse_key` vacío → direccionado por contenido (idéntica petición reutiliza;
  petición distinta no colapsa).
Cambiar de proveedor NO invalida assets de otros (provider/model en la clave).
**Lock por clave + doble verificación**: bajo concurrencia, claves idénticas se
generan una sola vez (reutilización determinista, sin trabajo duplicado).

## Salida

```
output/documentary/
  images/   S01.png … S26.png
  metadata/ S01.json …
  manifest.json   (documentary id, provider, timestamp, assets, cache hits/misses, failures, retries, duración)
```
El `manifest.json` es la fuente de verdad para etapas posteriores.

## Decisiones de diseño (para los próximos 10 años)
- **Frontera de ejecución única**: añadir/cambiar proveedor = nuevo adapter; ni
  VIS/VAI/VSC (arriba) ni Motion/Composer (abajo) cambian.
- **Normalización en el VPL**: los adapters devuelven bytes+metadatos; el VPL los
  normaliza a `GeneratedAsset` + persistencia.
- **Determinista y observable**: mock determinista; logging estructurado; manifest
  reproducible. `sleep` inyectable para tests sin esperas.
- **Concurrente y seguro**: workers + lock por clave (sin generación duplicada).

## Ejemplo
`python -m app.cli.generate_documentary` → 26 imágenes del documental "Coquito",
continuidad de escena preservada, localizaciones reutilizadas, manifest completo.
No renderiza vídeo (termina en la generación de imágenes).
