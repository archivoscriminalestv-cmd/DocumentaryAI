"""Registry público de los motores de DocumentaryAI (DCA).

Declarativo y manual (NO autodescubre nada): cada subsistema se describe por su contrato
público — dominio, responsabilidad, entradas/salidas/artefactos, dependencias, capacidades
producidas/consumidas, estado y documentación. ``UNKNOWN`` antes que inventar.
"""

from app.dca.models import Domain, Pipeline, Status, Subsystem

S = Status


def _subsystems() -> list[Subsystem]:
    return [
        # --- Aprendizaje / conocimiento --------------------------------------
        Subsystem("DLE", "learning", "Aprende conocimiento cinematográfico de documentales reales (observe-only)",
                  S.IMPLEMENTED, inputs=["youtube_url", "local_video"],
                  outputs=["documentary_knowledge"], artifacts=["knowledge/documentaries/"],
                  dependencies=[], produces=["cinematographic_knowledge"],
                  consumes=[], docs=["ADR-0008", "ADR-0009", "ADR-0010"]),
        Subsystem("DKS", "knowledge_synthesis", "Sintetiza el conocimiento del DLE en patrones de estilo",
                  S.IMPLEMENTED, inputs=["knowledge/documentaries/"], outputs=["knowledge/styles/"],
                  artifacts=["knowledge/styles/"], dependencies=["DLE"],
                  produces=["style_patterns"], consumes=["cinematographic_knowledge"], docs=[]),
        Subsystem("DLM", "observability", "Dashboard/monitor en vivo del aprendizaje masivo",
                  S.IMPLEMENTED, inputs=["progress_events"], outputs=["dashboard"],
                  dependencies=["DLE"], produces=["learning_dashboard"],
                  consumes=["cinematographic_knowledge"], docs=["ADR-0013"]),
        Subsystem("YIE", "intelligence", "Inteligencia de YouTube (vídeo/canal/SEO/miniatura/competitiva) antes del DLE",
                  S.IMPLEMENTED, inputs=["youtube_url"],
                  outputs=["knowledge/documentaries/<id>/youtube.json", "competitive.json"],
                  dependencies=[], produces=["youtube_intelligence"], consumes=[],
                  docs=["ADR-0011", "ADR-0012"]),
        Subsystem("Advisor", "analysis", "Analiza el corpus de conocimiento vs el pipeline y reporta huecos (read-only)",
                  S.IMPLEMENTED, inputs=["knowledge/styles/"], outputs=["output/advisor/"],
                  dependencies=["DKS"], produces=["production_gaps"],
                  consumes=["style_patterns"], docs=["ADR-0014"]),
        Subsystem("VUE", "visual_understanding", "Clasifica atributos visuales objetivos (composición/color/shot)",
                  S.NOT_INTEGRATED, inputs=["frames"], outputs=["output/vue/"],
                  dependencies=[], produces=["visual_attributes"], consumes=[], docs=["ADR-0015"]),
        Subsystem("RDA", "visual_understanding", "Extrae la gramática audiovisual (CinematicProfile) de un vídeo de referencia",
                  S.IMPLEMENTED, inputs=["reference_video"], outputs=["output/rda/"],
                  dependencies=[], produces=["cinematic_profile"], consumes=[], docs=[]),

        # --- Evidencia -------------------------------------------------------
        Subsystem("EAE", "evidence", "Planifica, descubre y organiza la evidencia de un caso (sin descargar binarios)",
                  S.IMPLEMENTED, inputs=["case_profile"],
                  outputs=["investigation_plan", "discovery_plan", "project_workspace"],
                  artifacts=["output/projects/<case>/"], dependencies=[],
                  produces=["investigation_plan", "discovery_plan"], consumes=[],
                  docs=["ADR-0016", "ADR-0017", "ADR-0018"]),
        Subsystem("ECE", "evidence", "Correlaciona evidencias (grafo), analiza cobertura, conflictos y candidatos de recreación",
                  S.IMPLEMENTED, inputs=["investigation_plan", "discovery_plan"],
                  outputs=["evidence_graph", "coverage_report", "recreation_candidates"],
                  dependencies=["EAE"], produces=["evidence_graph", "coverage_report",
                  "recreation_candidates"], consumes=["discovery_plan", "investigation_plan"],
                  docs=["ADR-0019"]),
        Subsystem("ERE", "evidence", "Evidence Research Engine: reúne evidencia pública en un EvidenceGraph reproducible",
                  S.IMPLEMENTED, inputs=["project_knowledge"], outputs=["output/evidence/"],
                  dependencies=[], produces=["evidence_research"], consumes=[], docs=[]),
        Subsystem("Dossier", "evidence", "Documentary Dossier: fuente de verdad estructurada del caso",
                  S.IMPLEMENTED, inputs=["evidence_research"], outputs=["documentary_dossier"],
                  dependencies=["ERE"], produces=["documentary_dossier"],
                  consumes=["evidence_research"], docs=[]),

        # --- Personaje -------------------------------------------------------
        Subsystem("CRE", "character", "Character Research Engine: construye la Character Bible de un personaje",
                  S.IMPLEMENTED, inputs=["character_request"], outputs=["character_bible"],
                  dependencies=[], produces=["character_bible"], consumes=[], docs=[]),
        Subsystem("CCE", "character", "Character Consistency Engine: identidad visual permanente (identity lock)",
                  S.IMPLEMENTED, inputs=["character_bible", "evidence_graph"],
                  outputs=["character_profile"], dependencies=["CRE"],
                  produces=["character_profile"], consumes=["character_bible"], docs=["ADR-0003"]),

        # --- Generación visual ----------------------------------------------
        Subsystem("VIS", "visual_generation", "Visual Intelligence System: Scene -> VisualTimeline (Shot[])",
                  S.IMPLEMENTED, inputs=["narrative_scenes", "cinematic_profile"],
                  outputs=["visual_timeline"], dependencies=["RDA"],
                  produces=["visual_timeline"], consumes=["cinematic_profile"], docs=[]),
        Subsystem("VAI", "visual_generation", "Visual AI Director: Shot -> VisualSpecification + ShotExecutionRequest",
                  S.IMPLEMENTED, inputs=["visual_timeline"], outputs=["visual_specification"],
                  dependencies=["VIS"], produces=["visual_specification"],
                  consumes=["visual_timeline"], docs=[]),
        Subsystem("SDE", "visual_generation", "Shot Diversity Engine: diversidad determinista de composiciones",
                  S.IMPLEMENTED, inputs=["visual_specification"], outputs=["shot_diversity"],
                  dependencies=["VAI"], produces=["shot_diversity"],
                  consumes=["visual_specification"], docs=["ADR-0005"]),
        Subsystem("VSC", "visual_generation", "Visual Scene Compiler: -> VisualGenerationRequest normalizada",
                  S.IMPLEMENTED, inputs=["visual_specification", "shot_diversity", "character_profile"],
                  outputs=["visual_generation_request"], dependencies=["VAI", "SDE", "CCE"],
                  produces=["visual_generation_request"],
                  consumes=["visual_specification", "shot_diversity", "character_profile"], docs=[]),
        Subsystem("VPL", "visual_generation", "Visual Provider Layer: request -> GeneratedAssets (adapters reales)",
                  S.IMPLEMENTED, inputs=["visual_generation_request"], outputs=["generated_assets"],
                  dependencies=["VSC"], produces=["generated_assets"],
                  consumes=["visual_generation_request"], docs=[]),
        Subsystem("ALR", "assets", "Asset Library & Reuse: biblioteca permanente content-addressed",
                  S.IMPLEMENTED, inputs=["generated_assets"], outputs=["library/"],
                  dependencies=["VPL"], produces=["asset_library"],
                  consumes=["generated_assets"], docs=["ADR-0004"]),
        Subsystem("CME", "motion", "Cinematic Motion Engine: MotionShot por plano (provider-agnostic)",
                  S.IMPLEMENTED, inputs=["visual_generation_request"], outputs=["motion_plan"],
                  dependencies=["VSC"], produces=["motion_plan"],
                  consumes=["visual_generation_request"], docs=["ADR-0006"]),
        Subsystem("MGL", "visual_generation", "Media Generation Layer: generación/almacén/reuso de medios",
                  S.IMPLEMENTED, inputs=["visual_generation_request"], outputs=["media_assets"],
                  dependencies=["VPL"], produces=["media_assets"],
                  consumes=["visual_generation_request"], docs=[]),

        # --- Ensamblaje ------------------------------------------------------
        Subsystem("Composer", "assembly", "Documentary Runtime: ejecuta el pipeline y produce el MP4 (FFmpeg)",
                  S.IMPLEMENTED, inputs=["generated_assets", "motion_plan", "narration"],
                  outputs=["documentary.mp4"], dependencies=["VPL", "CME"],
                  produces=["documentary_mp4"],
                  consumes=["generated_assets", "motion_plan", "narration"],
                  docs=["ADR-0007"]),
    ]


_DOMAINS = {
    "learning": "Adquisición de conocimiento",
    "knowledge_synthesis": "Síntesis de conocimiento",
    "intelligence": "Inteligencia competitiva",
    "analysis": "Análisis arquitectónico/producción",
    "visual_understanding": "Comprensión visual",
    "evidence": "Evidencia documental",
    "character": "Personajes",
    "visual_generation": "Generación visual",
    "assets": "Biblioteca de assets",
    "motion": "Movimiento de cámara",
    "assembly": "Ensamblaje / render",
    "observability": "Observabilidad",
}

_PIPELINES = [
    Pipeline("generation",
             ["EAE", "ECE", "ERE", "Dossier", "CRE", "CCE", "VIS", "VAI", "SDE",
              "VSC", "VPL", "ALR", "CME", "Composer"]),
    Pipeline("learning", ["YIE", "DLE", "DKS", "Advisor"]),
]


def build_subsystems() -> list[Subsystem]:
    return sorted(_subsystems(), key=lambda s: s.name)


def build_domains(subsystems: list[Subsystem]) -> list[Domain]:
    by_domain: dict[str, list[str]] = {}
    for s in subsystems:
        by_domain.setdefault(s.domain, []).append(s.name)
    return [Domain(name=d, subsystems=sorted(by_domain.get(d, [])))
            for d in sorted(by_domain)]


def build_pipelines() -> list[Pipeline]:
    return list(_PIPELINES)


def domain_label(domain: str) -> str:
    return _DOMAINS.get(domain, domain)
