"""Capability Matrix del AIM — qué capacidades ofrece cada proveedor (determinista)."""


def build_capability_matrix(registry) -> dict:
    by_capability: dict[str, list[str]] = {}
    by_provider: dict[str, list[str]] = {}
    for provider in registry.all():
        caps = sorted(provider.spec.capabilities)
        by_provider[provider.name] = caps
        for cap in caps:
            by_capability.setdefault(cap, []).append(provider.name)
    # cada capacidad: cadena de resolución (principal → alternativos) + estado del principal
    resolution: dict[str, dict] = {}
    for cap in sorted(by_capability):
        chain = registry.resolve(cap)
        primary = chain[0] if chain else None
        state = primary.health(probe=False).state if primary is not None else "UNKNOWN"
        resolution[cap] = {
            "providers": [p.name for p in chain],
            "primary": primary.name if primary else "UNKNOWN",
            "alternative": chain[1].name if len(chain) > 1 else "UNKNOWN",
            "status": state,
        }
    return {
        "by_capability": resolution,
        "by_provider": {k: by_provider[k] for k in sorted(by_provider)},
    }
