# gitops — Git Repository Sanitizer & Readiness (INF-003)

Utilidad de infraestructura **Git** que deja DocumentaryAI preparado para su **primer backup
histórico** en GitHub, con la garantía de subir **solo el proyecto limpio** (código,
documentación, arquitectura, tests, configuración) y **nunca** contenido generado, temporales,
cachés, secretos ni binarios pesados.

**No es un motor.** No aprende, no genera, no toca DLE/VIS/VAI/Composer/NAR/KBG/PCX/DCA/Studio/…
Solo **lee** el repositorio (git en modo lectura) y escribe informes en `output/system/`.
**Nunca** ejecuta `git add`, `git commit` ni `git push`.

## Qué hace

1. **Auditoría del árbol** — clasifica cada fichero: `SOURCE / CONFIG / KNOWLEDGE / DATASET /
   OUTPUT / TEMPORARY / GENERATED / CACHE / BINARIES / LARGE_FILES`.
2. **`.gitignore`** — comprueba (y opcionalmente añade, idempotente) las exclusiones recomendadas:
   `output/`, `workspace/`, `downloads/`, `renders/`, `render/`, `tmp/`, `logs/`, `*.log`,
   `*.tmp`, modelos (`*.pt/*.ckpt/*.safetensors/…`), archivos (`*.zip/*.7z/*.rar`), `*.exe/*.dll`,
   `channel_intro.mp4`… (respeta lo que ya tenías; solo añade lo que falta).
3. **Archivos grandes** — aviso ≥ 50 MB, **BLOQUEO ≥ 100 MB** (límite duro de GitHub). Informa
   ruta/tamaño/motivo; **nunca borra**.
4. **Secretos** — busca API keys, tokens, contraseñas y claves privadas en lo que se subiría, y
   verifica que `.env` sigue **ignorado**. Nunca imprime el valor del secreto.
5. **Verificación de estructura** — confirma que el commit no incluye `OUTPUT/GENERATED/CACHE/
   TEMPORARY`.
6. **Informe Git Readiness** — `output/system/git_readiness.json` + `git_readiness_report.md`
   con: estado git/GitHub, qué se subirá (por categoría y carpeta), archivos grandes, secretos,
   exclusiones que faltan, y el veredicto **listo para push**.

## Uso

```bash
# Informe (no modifica nada):
python -m app.cli.git_readiness

# Actualiza .gitignore con las exclusiones recomendadas que falten y luego informa:
python -m app.cli.git_readiness --write-gitignore
```

Cuando el informe diga **listo para push**, el primer backup es simplemente (lo haces tú):

```bash
git add .
git commit -m "First protected snapshot"
git push
```

## Módulos

`models.py` · `classifier.py` (ruta→categoría) · `git_status.py` (git solo-lectura, sin abrir
consola en Windows) · `large_files.py` (≥50 MB / ≥100 MB) · `secrets.py` (patrones + `.env`
ignorado) · `gitignore_manager.py` (añade lo que falta, idempotente) · `readiness.py` (veredicto)
· `persistence.py` (`output/system/`).

Ver `docs/adr/ADR-0031-Git-Repository-Sanitizer.md`.
