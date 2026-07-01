"""Persistencia del CCE: serializa el ``CharacterProfile`` y sus informes.

Reproducible (mismo input -> mismo JSON, ``sort_keys``); la marca temporal vive solo
en el manifest. Versionado vía ``schema_version`` dentro del perfil.
"""

import json
import os
import time

from app.cce.models import CharacterProfile
from app.cce.prompt_builder import IdentityPromptBuilder


def write_outputs(out_dir: str, profile: CharacterProfile, manifest: dict,
                  *, generated_at: float | None = None) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    profile_path = os.path.join(out_dir, "character_profile.json")
    manifest_path = os.path.join(out_dir, "profile_manifest.json")
    report_path = os.path.join(out_dir, "profile_report.md")

    with open(profile_path, "w", encoding="utf-8") as handle:
        json.dump(profile.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)

    manifest_out = dict(manifest)
    manifest_out["generated_at"] = generated_at if generated_at is not None else time.time()
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest_out, handle, ensure_ascii=False, indent=2)

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(_render_report(profile))

    return {"profile": profile_path, "manifest": manifest_path, "report": report_path}


def load_profile(path: str) -> CharacterProfile:
    with open(path, encoding="utf-8") as handle:
        return CharacterProfile.from_dict(json.load(handle))


def _render_report(profile: CharacterProfile) -> str:
    block = IdentityPromptBuilder().build_identity_block(profile)
    constraints = profile.visual_constraints or ["(none — partial profile)"]
    lines = [
        f"# Character Profile — {profile.canonical_name or '(unnamed)'}",
        "",
        f"- **Visual identity id:** `{profile.visual_identity_id or '—'}`",
        f"- **Schema version:** {profile.schema_version}",
        f"- **Completeness:** {profile.completeness:.0%} "
        f"({len(profile.attribute_values())}/{_total_attributes()} visual attributes)",
        f"- **Partial profile:** {'yes' if profile.is_partial() else 'no'}",
        f"- **Reference images registered:** {len(profile.reference_images)}",
        "",
        "## Identity block (provider-agnostic, prepended by the compiler)",
        "",
        "```",
        block,
        "```",
        "",
        "## Visual constraints",
        "",
        *[f"- {c}" for c in constraints],
        "",
        "## Continuity rules (derived)",
        "",
        "| Attribute | Severity | Value | Directive |",
        "|-----------|----------|-------|-----------|",
        *[f"| {r.attribute} | {r.severity} | {r.value or '—'} | {r.directive} |"
          for r in profile.continuity_rules],
        "",
        "## Negative constraints",
        "",
        ", ".join(profile.negative_constraints) or "(none)",
        "",
    ]
    if profile.reference_images:
        lines += ["## Reference images (registered, not downloaded)", "",
                  "| reference_id | provider | license | quality |",
                  "|--------------|----------|---------|--------:|"]
        lines += [f"| {r.reference_id or '—'} | {r.provider or '—'} | {r.license or '—'} | {r.quality:.2f} |"
                  for r in profile.reference_images]
        lines.append("")
    return "\n".join(lines)


def _total_attributes() -> int:
    from app.cce.models import VISUAL_ATTRIBUTES

    return len(VISUAL_ATTRIBUTES)
