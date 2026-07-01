"""Contrato de integración del CCE con el pipeline (capa ADITIVA).

El CCE nunca llama al VPL ni a un proveedor. Expone un CONTRATO: dado un
``CharacterProfile`` y una petición de generación ya compilada por el VSC, antepone el
bloque fijo de identidad al prompt y fusiona los negativos de identidad. Devuelve una
NUEVA petición del mismo tipo (no muta la original, no toca el código del VSC/VPL).

Así el compilador/CLI puede aplicar el perfil de forma transparente: el VSC y el VPL
siguen siendo EXACTAMENTE los mismos; lo único que cambia es que cada
``VisualGenerationRequest`` describe ahora a la misma persona.
"""

import dataclasses
from typing import Protocol

from app.cce.models import CharacterProfile
from app.cce.prompt_builder import IdentityPromptBuilder


class IdentityApplicator(Protocol):
    def apply(self, request, profile: CharacterProfile):
        ...


def _dedupe_csv(*csv_values: str) -> str:
    seen, out = set(), []
    for csv in csv_values:
        for token in str(csv or "").split(","):
            text = token.strip()
            key = text.lower()
            if text and key not in seen:
                seen.add(key)
                out.append(text)
    return ", ".join(out)


def apply_identity(request, profile: CharacterProfile, builder: IdentityPromptBuilder | None = None):
    """Devuelve una copia de ``request`` con el bloque de identidad antepuesto.

    El prompt del plano se conserva íntegro; el bloque de identidad va DELANTE (es la
    capa fija de identidad). Los negativos de identidad se fusionan con los del plano.
    """
    builder = builder or IdentityPromptBuilder()
    identity_block = builder.build_identity_block(profile)
    if not identity_block:
        return request

    new_prompt = f"{identity_block} {getattr(request, 'prompt', '')}".strip()
    new_negative = _dedupe_csv(getattr(request, "negative_prompt", ""),
                               builder.build_negative_block(profile))

    # dataclasses.replace mantiene el tipo exacto (VisualGenerationRequest u otro).
    if dataclasses.is_dataclass(request):
        return dataclasses.replace(request, prompt=new_prompt, negative_prompt=new_negative)
    # Fallback no-dataclass: muta defensivamente una copia superficial.
    import copy

    clone = copy.copy(request)
    setattr(clone, "prompt", new_prompt)
    setattr(clone, "negative_prompt", new_negative)
    return clone


def apply_identity_to_all(requests: list, profile: CharacterProfile,
                          builder: IdentityPromptBuilder | None = None) -> list:
    builder = builder or IdentityPromptBuilder()
    return [apply_identity(r, profile, builder) for r in requests]
