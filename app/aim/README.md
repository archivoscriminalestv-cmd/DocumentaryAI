# API Integration Manager (AIM) — `app/aim/`

El **único punto central** de DocumentaryAI para todas las conexiones externas. A partir de
aquí, **ningún motor habla directamente con una API**: pide una *capacidad* (p.ej. `image`,
`voice`, `llm`, `evidence`) y el AIM resuelve el proveedor (principal → alternativo). Esto
permite conectar cualquier proveedor en minutos **sin volver a tocar ningún motor**.

> Composición, determinista, sin IA, sin acoplar proveedores concretos a los motores. Sin
> llamadas reales salvo el Health Check opcional. Nunca imprime ni persiste credenciales. No
> modifica ningún otro subsistema. Ver `docs/adr/ADR-0024`.

## Componentes
- **registry.py** — registro PÚBLICO y declarativo de proveedores (`ProviderSpec`: nombre,
  categoría, estado, versión, documentación, capacidades, requiere clave, límites, coste,
  timeout, retries, prioridad, alternativo). Resuelve capacidad → cadena por prioridad.
- **interfaces.py** — Protocols por capacidad (LLM/Image/Video/Voice/Music/OCR/Embedding/
  Translation/Evidence/Maps), independientes del proveedor concreto.
- **secrets.py** — `SecretManager`: busca credenciales en entorno → `.env` → config. Nunca
  hardcodea, nunca imprime, nunca persiste; solo informa de si están configuradas.
- **providers.py** — `ContractProvider.health()`: comprueba credenciales/integración sin
  descargar contenido; `prober` inyectable para conectividad real (latencia).
- **health.py / capability_matrix.py / readiness.py** — Health Check, matriz de capacidades y
  Production Readiness Checker (learning/evidence/generation/knowledge).
- **orchestrator.py** — `APIIntegrationManager`: providers/resolve/primary/capability_matrix/
  health_report/readiness.
- **persistence.py** — escribe en `output/system/`.

## CLI
```
python -m app.cli.system_check
# -> output/system/{production_readiness, providers, health_report, capability_matrix}.json
#    + informe ASCII (qué hay, qué tiene credenciales, qué está integrado, alternativos, pendientes)
```

## Cómo añadir un proveedor (en minutos, sin tocar motores)
1. Añade un `ProviderSpec` a `registry._specs()` (capacidades, clave si aplica, prioridad,
   alternativo).
2. (Cuando toque) implementa su adaptador (Protocol de su capacidad + `health()` real).
3. Los motores ya lo usan automáticamente vía `AIM.resolve(capacidad)` — sin cambios en ellos.

## Adaptadores reales (AIM-002)
`app/aim/adapters/`: cada adaptador implementa **el mismo contrato** (`health/capabilities/
authenticate/execute/cost/limits/provider_name/version`) heredando de `AdapterBase` (sin lógica
duplicada). Implementados: **OpenAI** (LLM/embeddings/images), **ElevenLabs** (voz), **Runway**
(vídeo), **Replicate** (imagen/vídeo), **Wikipedia/Wikidata/Wikimedia/Internet Archive**
(búsqueda), **OpenStreetMap** (geocoding). Errores **clasificados** (AUTH/TIMEOUT/QUOTA/
RATE_LIMIT/SERVICE_DOWN/INVALID_RESPONSE/UNAVAILABLE), **retries exponenciales acotados**,
**circuit breaker** y **métricas objetivas** (proveedor/operación/tiempo/éxito/retries/coste —
nunca prompts ni credenciales). HTTP inyectable (`app/aim/http.py`).

Los motores piden una capacidad y el AIM ejecuta con fallback automático:
```python
AIM.execute("image", "generate_image", prompt=...)   # runway/openai → replicate → ... → UNKNOWN
```
`python -m app.cli.system_check --probe` hace una llamada mínima REAL (cuando hay credencial)
para verificar conectividad; sin `--probe` es offline/determinista. Añadir un proveedor nuevo =
un adaptador + un `ProviderSpec`, **sin tocar ningún motor**. Ver `docs/adr/ADR-0025`.

## Estado
Este sprint construye la infraestructura permanente. Los proveedores de evidencia públicos
(Wikipedia/Wikidata/Commons/Internet Archive/OSM/LoC/National Archives) y locales (yt-dlp,
SAPI) figuran como usables; OpenAI/Anthropic/ElevenLabs/Runway/… quedan declarados, listos para
integrarse uno a uno aportando su credencial y adaptador.
