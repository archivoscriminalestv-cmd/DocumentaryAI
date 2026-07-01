# ADR-0031 — Git Repository Sanitizer & First Safe Backup

- **Status:** Accepted
- **Date:** 2026-07-01
- **Sprint:** INF-003
- **Relates:** ADR-0028 (Infrastructure Protection), ADR-0010/0016 (temporary binaries policy)

## Contexto

El repositorio Git existe y está conectado a GitHub, pero solo hay 10 ficheros seguidos y
**cientos de archivos nuevos sin revisar**. Antes del primer commit histórico hay que garantizar
que GitHub contendrá **solo el proyecto limpio** (código, docs, arquitectura, tests, config) y
nunca contenido generado, temporales, cachés, secretos ni binarios pesados.

## Decisión 1 — Utilidad Git separada, sin tocar motores

Se crea `app/gitops/` (no un motor: no aprende ni genera). Lee el repo con git en **modo lectura**
y escribe informes en `output/system/`. **Nunca** ejecuta `git add/commit/push`. No modifica
DLE/DKS/YIE/VAI/VIS/Composer/AIM/NAR/KBG/PCX/Studio/DCA ni comportamiento funcional. Se ubica
fuera de `app/infra/` a propósito: el test existente de INF prohíbe importar `subprocess`/`git` en
`app.infra`, y no se pueden modificar tests existentes.

## Decisión 2 — Auditoría por categorías + veredicto objetivo

Cada fichero del conjunto que `git add .` subiría se clasifica en `SOURCE / CONFIG / KNOWLEDGE /
DATASET / OUTPUT / TEMPORARY / GENERATED / CACHE / BINARIES / LARGE_FILES`. El repo se declara
**listo para push** solo si: es repo git, `.env` está ignorado, no hay secretos ERROR, no hay
ficheros ≥ 100 MB en el commit, y **no** se subiría nada `OUTPUT/GENERATED/CACHE/TEMPORARY`.

## Decisión 3 — `.gitignore` idempotente y no destructivo

`gitignore_manager` solo **añade** las exclusiones recomendadas que falten (bajo un bloque
marcado); nunca borra ni reordena lo del usuario. Se añadieron: `output/`, `workspace/`,
`downloads/`, `renders/`, `render/`, `tmp/`, `logs/`, `*.log`, `*.tmp`, modelos
(`*.pt/*.ckpt/*.safetensors/*.onnx/*.gguf`), archivos (`*.zip/*.7z/*.rar`), `*.exe/*.dll` y
`/channel_intro.mp4`. (`outputs/`, `cache/`, `knowledge/`, `library/`, `archive/`, `.env*` ya
estaban.)

## Decisión 4 — Archivos grandes y límite de GitHub

Aviso ≥ 50 MB y **bloqueo ≥ 100 MB** (GitHub rechaza el push de ficheros así en un repo normal).
Se informa ruta/tamaño/motivo y **nunca** se borra nada. Verificación real: **0 ficheros > 100 MB**
en el proyecto.

## Decisión 5 — Secretos, con filtrado de falsos positivos

Se escanean solo los ficheros de texto que se subirían buscando claves privadas, `sk-`, AWS,
Google, HuggingFace, Slack y asignaciones genéricas. Se descartan **nombres de variable/entorno**
(p. ej. `requires_api_key="REPLICATE_API_TOKEN"`) y placeholders de `.env.example`. Se verifica que
`.env` sigue **ignorado** (lo está).

## Consecuencias

- **Positivo:** tras el sprint, `git add .` pasa de **1132 → 743** ficheros nuevos: solo `SOURCE`
  (745), `CONFIG` (6), `DATASET` (1, el .txt de URLs) y **1** binario de 6.7 KB
  (`assets/fallback/gray.mp4`, fixture de código). Cero OUTPUT/TEMP/GENERATED/CACHE, cero secretos,
  cero > 100 MB → **listo para push**. El usuario hace el primer commit a mano con tranquilidad.
- **Limitaciones aceptadas:** `assets/fallback/gray.mp4` es un vídeo diminuto pero se **mantiene**
  por ser un fixture necesario para restaurar el proyecto completo (se informa para que el usuario
  decida). `channel_intro.mp4` (branding) se **excluye** de git y debe respaldarse vía INF (backup
  externo), coherente con "los binarios se respaldan aparte, no en git".

## Prueba

`git check-ignore` confirma ignorados `output/`, `channel_intro.mp4`, `cache/`, `.env`, `logs/`,
`tmp/`. Informe: `output/system/git_readiness.json` + `git_readiness_report.md`. Tests
`tests/test_gitops.py` 6/6 (clasificador, `.gitignore` idempotente/no destructivo, umbral
50/100 MB, detección de secretos + descarte de falsos positivos, e integración real con git:
`OUTPUT` bloquea → tras ignorar `output/` queda limpio).
```
git add .
git commit -m "First protected snapshot"
git push
```
