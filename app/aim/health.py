"""Health Check del AIM — comprueba cada proveedor sin descargar contenido.

Llama a ``provider.health(prober=...)``. Por defecto NO hay red (estado reproducible basado
en credenciales + integración). Con un ``prober`` inyectable se mide conectividad/latencia.
"""


def check_all(registry, *, probe: bool = False) -> list:
    return [p.health(probe=probe) for p in registry.all()]


def summarize(statuses) -> dict:
    by_state: dict[str, int] = {}
    for s in statuses:
        by_state[s.state] = by_state.get(s.state, 0) + 1
    return {"providers": len(statuses), "by_state": {k: by_state[k] for k in sorted(by_state)}}
