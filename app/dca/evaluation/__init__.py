"""DCA Self Evaluation Engine (DCA-003) — `app/dca/evaluation/`.

Cierra el ciclo Generación → Aprendizaje: compara OBJETIVAMENTE el documental generado con
el conocimiento aprendido del corpus, convierte las diferencias en huecos, mapea cada hueco a
su motor responsable, y genera un roadmap + indicadores de salud del sistema.

NO usa IA, NO puntúa subjetivamente, NO dice "es bueno/malo": solo mide hechos. Solo lectura
de contratos públicos (GenerationKnowledge/ProductionContext/VisualPlan/Evidence Coverage/
Recreation Candidates/Knowledge Styles). Determinista. `UNKNOWN` antes que inventar. Es una
capacidad NUEVA del DCA, no un motor independiente.
"""

EVAL_SCHEMA_VERSION = "0.1"
EVAL_VERSION = "DCA-003"
