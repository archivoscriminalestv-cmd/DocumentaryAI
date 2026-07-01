# Production Context (PCX) — `app/pcx/`

`ProductionContext` es el **contrato arquitectónico permanente** y la **frontera entre
Knowledge y Generation**:

```
Knowledge (DLE → DKS / YIE / VUE / EAE → ECE → KBG → GenerationKnowledge)
        │
        ▼
  ProductionContextBuilder  →  ProductionContext   ← contrato único
        │
        ▼
Generation (VIS → VAI → Composer → Narration → Music → …)
```

A partir de PCX, **los motores de generación solo conocen `ProductionContext`**: nunca leen
KBG ni `knowledge/`, ni conocen DLE/DKS/EAE/ECE ni ningún otro subsistema. Esto evita
dependencias cruzadas y futuras refactorizaciones: PCX es el lenguaje común.

> Subsistema diminuto y desacoplado. NO decide nada; solo CONSTRUYE el contexto.
> Determinista, provider-agnóstico, solo lectura, `UNKNOWN` antes que inventar. No persiste
> (vive en memoria). Ver `docs/adr/ADR-0022`.

## Componentes
- **models.py** — `ProductionContext` (+ `DecisionView`). Hoy contiene `generation`
  (decisiones conocidas del KBG, ya sin `UNKNOWN`) y deja **reservados** (sin implementar):
  evidence_coverage, recreation_policy, project_constraints, target_platform, duration,
  audience, language, case_metadata, production_preferences, user_preferences.
- **interfaces.py** — `ProductionContextLike` (Protocol): lo único que un motor necesita
  (`has` / `get`).
- **loader.py** — convierte `GenerationKnowledge` (objeto o JSON) en decisiones neutrales,
  **ignorando UNKNOWN**; tolera artefactos inexistentes.
- **builder.py** — `ProductionContextBuilder.build(...)`: carga, ignora UNKNOWN, construye un
  contexto determinista; nunca inventa.

## API que usan los motores
```python
ctx.get("storytelling", "average_shot_duration")   # valor o None (None si UNKNOWN/ausente)
ctx.get("cinematography", "color_temperature", min_confidence=0.4)
ctx.has("cinematography", "lighting")
```
Una decisión solo se aplica si **existe, es conocida y tiene confianza suficiente**; en
cualquier otro caso el motor se comporta exactamente igual que antes.
