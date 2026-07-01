# Character Research Engine (CRE) — `app/cre/`

Subsistema **aditivo** e independiente que transforma un personaje conocido en una
**Character Bible** estructurada (la *fuente de verdad* de ese personaje). Es
genérico (Tesla, Picasso, Marie Curie, cualquier figura pública), determinista,
provider-agnostic, serializable y versionado.

> Este subsistema **no** genera imágenes ni prompts, **no** mantiene consistencia
> visual y **no** modifica VIS/VAI/VSC/VPL/Motion/Composer/FFmpeg. Solo investiga y
> estructura conocimiento.

## Pipeline
```
CharacterRequest → ResearchOrchestrator → [N ResearchProviders] → ResearchNormalizer → CharacterBible
                                                                                      ↘ research_manifest
                                                                                      ↘ research_report.md
```

## Proveedores (CRE-002)
Catálogos en `app/cre/orchestrator.py`:
- **`real_providers(client, lang)`** (producción / CLI por defecto):
  - **WikipediaProvider** (`providers/wikipedia.py`): nombre canónico + extracto
    biográfico (REST API `/page/summary`). Confianza 0.8.
  - **WikidataProvider** (`providers/wikidata.py`): datos estructurados verificables
    — nacimiento/defunción (P569/P570), ocupación (P106), nacionalidad (P27) con
    resolución de etiquetas. Confianza 0.9.
  - **CommonsProvider** (`providers/commons.py`): cataloga `visual_references`
    (URL, licencia, autor, descripción, resolución, quality_score) **sin descargar
    imágenes** (`hash` reservado). Confianza 0.7.
  - **NewsProvider / ArchiveProvider** (`providers/external.py`): interfaz preparada
    (`available=False`).
  - **MockResearchProvider**: red de seguridad determinista (confianza 0.2).
- **`default_providers()`** (offline/determinista): stubs + mock; lo usan los tests.

La red está aislada tras `HttpClient` (`app/cre/http.py`) e **inyectable**: en los
tests se pasa un cliente falso → cero llamadas reales y determinismo total.

## Modelo de datos
- **CharacterRequest**: `name`, `aliases`, `hints` (pistas explícitas; nunca inventa).
- **CharacterBible** (`schema_version`): `identity`, `biography` (incl. `summary`),
  `physical_appearance`, `behaviour`, `voice`, `environment`, `visual_references[]`,
  `sources[]`, `providers_used[]`, **`provenance[]`**, **`conflicts[]`**.
- **VisualReference**: `id`, `provider`, `url`, `license`, `copyright`, `author`,
  `caption`, `description`, `resolution`, `quality_score`, `relevance_score`, `hash`
  (+ `source` legado). La Bible puede contener decenas de referencias.
- Serialización: `to_dict()/from_dict()`; JSON con `sort_keys` (reproducible). La
  marca temporal vive **solo** en el manifest.

## Modelo de confianza y trazabilidad (CRE-002)
Cada `ResearchResult` lleva una `confidence` (fiabilidad del proveedor). El
Normalizer es **determinista**:
- **escalares**: gana el de mayor `confidence`; a igualdad, el primer proveedor en
  orden (compatibilidad "primer no vacío gana"),
- **listas**: dedupe preservando orden,
- **provenance**: por cada dato escogido se registra `{field, value, provider,
  confidence}` → la Bible **nunca contiene un hecho sin origen conocido**,
- **conflicts**: cuando varias fuentes discrepan en un escalar se guardan **todos**
  los candidatos (valor + proveedor + confianza); **no se fusiona arbitrariamente**.

## research_manifest.json
Proveedores consultados, disponibilidad, `confidence`, secciones aportadas, nº de
referencias, errores, `elapsed_ms`, `versions` (schema + cre), `character_id`,
`totals` y `generated_at` (sello temporal).

## Cómo añadir un proveedor nuevo
1. Implementa `ResearchProvider` (`app/cre/providers/base.py`). Si usa red, recibe un
   `HttpClient` inyectable y emite una `confidence`:
   ```python
   class MyProvider(ResearchProvider):
       name = "my-source"
       def __init__(self, client=None):
           self._client = client or JsonHttpClient()
       def research(self, request):
           try:
               raw = self._client.get_json("https://...", {"q": request.name})
           except Exception as exc:
               return ResearchResult(self.name, False, error=str(exc))
           return ResearchResult(self.name, True,
                                 data={"identity": {"occupation": raw["job"]}},
                                 sources=["https://..."], confidence=0.85)
   ```
2. Añádelo a `real_providers()` (o pásalo a `ResearchOrchestrator([...])`).
3. **No** hay que tocar el orquestador, el normalizer ni el resto del sistema. La
   normalización por confianza y la trazabilidad funcionan automáticamente.

## Decisiones arquitectónicas (CRE-001)
- **AD-1 — Provider-agnostic + plug-in:** la investigación se abstrae tras
  `ResearchProvider`; el orquestador no conoce ninguna fuente concreta. Permite
  añadir Wikipedia/News/Archive/imágenes durante años sin refactor.
- **AD-2 — Bible como fuente de verdad versionada y reproducible:** `schema_version`
  + JSON `sort_keys` + sin timestamp en la bible. Habilita difs estables y evolución
  de esquema controlada.
- **AD-3 — Fusión determinista en el Normalizer:** escalares "primer no vacío gana",
  listas dedupe-en-orden. Misma entrada → misma bible.
- **AD-4 — Sin fabricación de hechos:** sin proveedores reales, el motor emite un
  esqueleto con la identidad del request y deja el resto vacío; nunca inventa datos
  sobre personas reales. Los proveedores reales rellenarán datos verificados.
- **AD-5 — Separación manifest/bible:** la traza temporal y de proveedores va al
  manifest; la bible permanece reproducible.

## Decisiones arquitectónicas (CRE-002)
- **AD-6 — Red aislada e inyectable (`HttpClient`):** los proveedores reales no
  dependen de un cliente concreto; reciben un `HttpClient`. Permite mockear el 100%
  de las llamadas externas → tests deterministas sin red, y cambiar la capa de
  transporte sin tocar la lógica.
- **AD-7 — Confianza por proveedor + provenance:** cada dato escogido es trazable a
  su fuente con un nivel de confianza. La Bible nunca contiene hechos sin origen.
- **AD-8 — Conflictos sin fusión arbitraria:** ante discrepancia entre fuentes se
  conservan todos los candidatos en `conflicts`; el motor no inventa un "consenso".
- **AD-9 — Referencias visuales sin descarga:** Commons cataloga URL+licencia+
  metadatos; `hash` queda reservado para una futura descarga. Respeta copyright y la
  frontera "el CRE no genera imágenes".
- **AD-10 — Degradación limpia y aditiva:** un proveedor que falla devuelve
  `available=False` + `error` (queda en el manifest) y no rompe el pipeline; los dos
  catálogos (`default_providers`/`real_providers`) conviven sin romper CRE-001.

## CLI
```
python -m app.cli.research_character --name "Nikola Tesla"     # fuentes reales (def.)
python -m app.cli.research_character --name "Coquito" --offline # solo stubs + mock
python -m app.cli.research_character --name "Picasso" --lang es # idioma de fuentes
# -> output/research/<slug>/{character_bible.json, research_manifest.json, research_report.md}
```

## Preparado para el Character Consistency Engine (futuro)
La Bible es la entrada estable que un futuro *Character Consistency Engine* (CCE)
consumirá: `physical_appearance`, `behaviour`, `voice`, `environment` y
`visual_references` ya existen como contrato; el CCE podrá derivar de ahí prompts y
locks de consistencia **sin** rediseñar el CRE (solo lee la Bible versionada).
