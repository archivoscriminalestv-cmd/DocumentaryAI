"""Character Consistency Engine (CCE) — Sprint CCE-001.

Subsistema ADITIVO e independiente. Transforma una ``CharacterBible`` (CRE) —y,
opcionalmente, un ``EvidenceGraph`` (ERE)— en un ``CharacterProfile``: la identidad
VISUAL permanente del personaje. El CCE NO genera imágenes, NO genera prompts de
plano y NO llama al VPL ni a ningún proveedor: solo produce RESTRICCIONES
cinematográficas (provider-agnósticas) que el resto del pipeline respetará.

Flujo:  CharacterBible (+ EvidenceGraph) → IdentityLockEngine → CharacterProfile →
(contrato) aplicado por el compilador a cada VisualGenerationRequest.

Garantía de diseño: el mismo input produce el mismo ``CharacterProfile`` (determinista,
serializable, versionado). La arquitectura queda preparada para el futuro
(embeddings, LoRA, IP-Adapter) sin rediseño: la comparación de identidad se hace por
una interfaz ``ProfileComparator`` y las referencias visuales ya tienen modelo.
"""

SCHEMA_VERSION = "1.0"

from app.cce.consistency import (
    AttributeProfileComparator,
    IdentityConsistencyScore,
    IdentityConsistencyScorer,
    ProfileComparator,
)
from app.cce.continuity import derive_continuity_rules
from app.cce.identity_lock import IdentityLockEngine
from app.cce.integration import IdentityApplicator, apply_identity, apply_identity_to_all
from app.cce.models import (
    CharacterProfile,
    ContinuityRule,
    ReferenceImage,
)
from app.cce.prompt_builder import IdentityPromptBuilder

__all__ = [
    "SCHEMA_VERSION",
    "CharacterProfile",
    "ContinuityRule",
    "ReferenceImage",
    "IdentityLockEngine",
    "derive_continuity_rules",
    "IdentityPromptBuilder",
    "IdentityConsistencyScore",
    "IdentityConsistencyScorer",
    "ProfileComparator",
    "AttributeProfileComparator",
    "IdentityApplicator",
    "apply_identity",
    "apply_identity_to_all",
]
