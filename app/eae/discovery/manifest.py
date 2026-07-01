"""Constructor del manifest rico de descubrimiento (EAE-003).

Genera una ``DiscoveryManifest`` con una entrada por evidencia descubierta: origen, cadena
de custodia, estado, duplicados, hash, licencia, uso permitido, proveedor, descargado/
validado y relaciones (personas/lugares/eventos). Determinista; nada se inventa.
"""

from app.eae import UNKNOWN
from app.eae.discovery.models import DiscoveryManifest, ManifestEntry


def _permitted_use(license_name: str) -> str:
    name = (license_name or "").upper()
    if name in ("PUBLIC_DOMAIN", "CC0"):
        return "free"
    if name.startswith("CC-BY"):
        return "attribution_required"
    if name in ("RIGHTS_RESERVED", "ODBL"):
        return "restricted" if name == "RIGHTS_RESERVED" else "attribution_share_alike"
    return UNKNOWN


def _provider_cost(discovery_plan, provider: str) -> str:
    for need in discovery_plan.needs:
        for d in need.provider_decisions:
            if d.get("provider") == provider:
                return d.get("cost", UNKNOWN)
    return UNKNOWN


def build_manifest(plan, discovery_plan) -> DiscoveryManifest:
    people = set(plan.profile.people if plan.profile else [])
    locations = set(plan.profile.locations if plan.profile else [])
    events = set(plan.profile.events if plan.profile else [])

    # reason de selección por (need, provider) para auditar cada evidencia
    reason_by = {}
    for need in discovery_plan.needs:
        for d in need.provider_decisions:
            reason_by[(need.need_id, d["provider"])] = d["reason"]

    entries: list[ManifestEntry] = []
    for ev in discovery_plan.discovered:
        target = ev.target
        entries.append(ManifestEntry(
            evidence_id=ev.id, category=ev.category, target=target, provider=ev.provider,
            origin=ev.url or ev.provider,
            chain_of_custody=[f"discovered:{ev.provider}"] + ([f"url:{ev.url}"] if ev.url else []),
            status="DISCOVERED", downloaded=False, validated=False,
            duplicates=[], hash=ev.hash, license=ev.license,
            permitted_use=_permitted_use(ev.license),
            cross_references=[ev.need_id] if ev.need_id else [],
            related_people=[target] if target in people else [],
            related_locations=[target] if target in locations else [],
            related_events=[target] if target in events else [],
            query_used=list(ev.query_used),
            selection_reason=reason_by.get((ev.need_id, ev.provider), ""),
        ))

    provider_audit = [
        {"provider": name, "results": discovery_plan.by_provider[name],
         "search_ms": discovery_plan.timings.get(name, 0.0),
         "cost": _provider_cost(discovery_plan, name)}
        for name in sorted(discovery_plan.by_provider)
    ]

    pending = [n.need_id for n in discovery_plan.needs if n.discovered < n.minimum]
    return DiscoveryManifest(
        case_id=plan.case_id, title=discovery_plan.title,
        totals=discovery_plan.totals, entries=entries, pending_needs=pending,
        people=sorted(people), locations=sorted(locations),
        timeline=list(plan.profile.events if plan.profile else []),
        provider_audit=provider_audit,
    )
