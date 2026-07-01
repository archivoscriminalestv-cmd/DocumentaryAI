# CCE — Character Consistency Engine

Subsistema **aditivo** que garantiza que un documental muestre **a la misma persona**
en todos los planos. Convierte la `CharacterBible` (CRE) —y, opcionalmente, el
`EvidenceGraph` (ERE)— en un `CharacterProfile`: la **identidad visual permanente** del
personaje, expresada como **restricciones cinematográficas provider-agnósticas**.

El CCE **no** genera imágenes, **no** genera prompts de plano, **no** llama al VPL ni a
ningún proveedor, y **no** modifica VIS/VAI/VSC/VPL/Motion/Composer/FFmpeg.

```
CharacterBible (+ EvidenceGraph)
        │
        ▼
IdentityLockEngine        →  CharacterProfile (identidad visual permanente)
        │                        ├─ visual_identity_id (estable, derivado del nombre)
        │                        ├─ atributos visuales (solo los conocidos)
        │                        ├─ continuity_rules (derivadas)
        │                        ├─ visual_constraints / negative_constraints
        │                        └─ reference_images (registradas, sin descargar)
        ▼
IdentityPromptBuilder     →  bloque de identidad (lenguaje neutro)
        │
        ▼
apply_identity (contrato)  →  antepone el bloque a cada VisualGenerationRequest
                              (VSC y VPL intactos; solo cambia el prompt)
```

## Módulos (`app/cce/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `models.py` | `CharacterProfile`, `ReferenceImage`, `ContinuityRule`; `VISUAL_ATTRIBUTES`, `MUTABLE_ATTRIBUTES`, `visual_identity_id()` |
| `identity_lock.py` | `IdentityLockEngine`: Bible (+Evidence) → `CharacterProfile` determinista (nunca inventa) |
| `continuity.py` | `derive_continuity_rules()`: reglas locked/soft derivadas del perfil |
| `prompt_builder.py` | `IdentityPromptBuilder`: bloque de identidad + negativos, construidos desde el perfil |
| `consistency.py` | `IdentityConsistencyScorer` + `ProfileComparator` (por atributos hoy, embeddings mañana) |
| `integration.py` | Contrato `apply_identity` / `apply_identity_to_all`: aplica el perfil a las peticiones |
| `persistence.py` | Serialización del perfil + manifest + report (reproducible, versionado) |

## Decisiones arquitectónicas

- **Identidad permanente, no por proveedor.** `visual_identity_id` se deriva del nombre
  canónico (hash estable). El mismo personaje produce siempre el mismo id, en cualquier
  proveedor. Ver `ADR-0003`.
- **Integración por contrato, sin tocar el VSC.** El CCE expone `apply_identity`; el
  CLI/compilador lo invoca tras el VSC para anteponer el bloque fijo de identidad. VSC y
  VPL no cambian. Ver `ADR-0003`.
- **Nunca inventar.** Solo se vuelcan atributos presentes en la bible. Un personaje con
  pocos datos (p.ej. Coquito) produce un **perfil parcial**: el bloque contiene solo
  directivas de estabilidad ("misma persona", "no rediseñar", "proporciones fijas").
- **Provider-agnostic.** Ni el perfil ni el bloque contienen sintaxis de proveedor; los
  adapters del VPL traducirán si lo necesitan.
- **Embedding-ready.** La comparación de identidad está detrás de `ProfileComparator`; un
  futuro `EmbeddingProfileComparator` (rostros) se enchufa sin tocar el resto.

## Cómo añadir un nuevo origen de identidad / comparador

- **Otro comparador de consistencia** (p.ej. embeddings): implementa
  `ProfileComparator.compare(a, b) -> IdentityConsistencyScore` e inyéctalo en
  `IdentityConsistencyScorer(comparator=...)`. Nada más cambia.
- **Otro origen de datos** (además de CRE/ERE): mapea tus datos a un `CharacterBible`
  (o pasa un objeto con los mismos atributos) y entrégalo a `IdentityLockEngine.lock()`.

## Modelo de datos (resumen)

`CharacterProfile` = identidad (`canonical_name`, `visual_identity_id`) + atributos
visuales escalares (edad, piel, ojos, pelo, barba, cara, nariz, etc.) + listas
(`typical_emotions`, `accessories`, `dominant_colors`) + `reference_images` +
`visual_constraints` + `negative_constraints` + `continuity_rules` + `completeness`.
Serializable (`to_dict`/`from_dict`), versionado (`schema_version`).

## CLI

```bash
python -m app.cli.build_character_profile --name "Coquito"
python -m app.cli.build_character_profile --name "Nikola Tesla"
# -> output/cce/<slug>/{character_profile.json, profile_manifest.json, profile_report.md}
```

En el render completo, `python -m app.cli.generate_documentary` aplica el perfil a los
26 planos automáticamente (el bloque de identidad va al frente de cada prompt).

## Preparado para el Character Consistency Engine "duro" (futuro)

El `CharacterProfile` ya define `reference_images` (id/provider/license/url/hash/quality)
y `visual_identity_id`. Cuando se añadan embeddings/LoRA/IP-Adapter, la identidad ya
existe como contrato estable: solo se sustituye el `ProfileComparator` y se rellenan las
referencias — **sin rediseñar** el subsistema ni el pipeline.
