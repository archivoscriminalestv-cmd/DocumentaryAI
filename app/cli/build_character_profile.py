"""Construye el CharacterProfile (CCE) de un personaje a partir de su CharacterBible.

    python -m app.cli.build_character_profile --name "Coquito"
    python -m app.cli.build_character_profile --name "Nikola Tesla"

Carga la CharacterBible del CRE si existe (``output/research/<slug>/character_bible.json``);
si no, parte de una bible vacía con solo el nombre (perfil PARCIAL, sin inventar nada).
Genera ``output/cce/<slug>/{character_profile.json, profile_manifest.json, profile_report.md}``.
"""

import argparse
import json
import os
import sys

from app.cce import IdentityLockEngine
from app.cce.models import slugify
from app.cce.persistence import write_outputs
from app.cce.prompt_builder import IdentityPromptBuilder
from app.cre.models import CharacterBible, Identity


def load_character_bible(name: str) -> CharacterBible:
    """Bible del CRE si existe; si no, una bible vacía solo con el nombre."""
    slug = slugify(name)
    path = os.path.join("output", "research", slug, "character_bible.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                return CharacterBible.from_dict(json.load(handle))
        except Exception:
            pass
    return CharacterBible(identity=Identity(id=f"character:{slug}", canonical_name=name))


def run(name: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    bible = load_character_bible(name)
    profile = IdentityLockEngine().lock(bible)
    out_dir = os.path.join("output", "cce", slugify(name))
    manifest = {
        "character": name,
        "visual_identity_id": profile.visual_identity_id,
        "schema_version": profile.schema_version,
        "completeness": profile.completeness,
        "known_attributes": profile.known_attributes,
        "source": "cre_bible" if profile.known_attributes else "name_only",
    }
    paths = write_outputs(out_dir, profile, manifest)

    print(f"[CCE] {name} -> {profile.visual_identity_id} "
          f"(completeness {profile.completeness:.0%}, {len(profile.continuity_rules)} continuity rules)")
    print("\n=== IDENTITY BLOCK ===")
    print(IdentityPromptBuilder().build_identity_block(profile))
    print(f"\nProfile:  {paths['profile']}\nReport:   {paths['report']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a CharacterProfile (CCE).")
    parser.add_argument("--name", default="Coquito", help="Character name")
    args = parser.parse_args()
    run(args.name)


if __name__ == "__main__":
    main()
