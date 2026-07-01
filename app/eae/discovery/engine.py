"""Case Discovery Engine (EAE-003/004).

``InvestigationPlan`` → ``DiscoveryPlan``. Por necesidad: el resolver selecciona proveedores
por capacidad/licencia/coste/fiabilidad (sin hardcodear), se consulta a los DISPONIBLES
(descubrir, NO descargar; cache a nivel de proveedor evita repetir búsquedas), y se agrega
cobertura. Registra auditoría por proveedor (resultados, motivo de selección/descarte) y
tiempos de búsqueda. Determinista en los resultados (orden estable; los tiempos no entran en
``to_dict``).
"""

import time

from app.eae.discovery.models import (
    DiscoveredEvidence,
    DiscoveryPlan,
    DiscoveryState,
    NeedCoverage,
)
from app.eae.discovery.providers.base import DiscoveryQuery
from app.eae.discovery.registry import SourceRegistry, default_registry
from app.eae.discovery.resolver import SourceResolver


class CaseDiscoveryEngine:
    def __init__(self, registry: SourceRegistry | None = None, *, language: str = "en",
                 max_cost: str | None = None, min_reliability: str | None = None) -> None:
        self._registry = registry or default_registry()
        self._resolver = SourceResolver(self._registry)
        self._language = language
        self._max_cost = max_cost
        self._min_reliability = min_reliability

    def discover(self, plan) -> DiscoveryPlan:
        licenses = list(plan.manifest.licenses) if plan.manifest else []
        terms_by_need = {t.need_id: t.query_terms for t in plan.search_tasks}

        needs_cov: list[NeedCoverage] = []
        discovered: list[DiscoveredEvidence] = []
        consulted: set[str] = set()
        timings: dict[str, float] = {}
        by_provider: dict[str, int] = {}

        for need in plan.needs:
            selected, discarded = self._resolver.select(
                need.category, license_requirements=licenses,
                max_cost=self._max_cost, min_reliability=self._min_reliability)
            query = DiscoveryQuery(
                case_id=plan.case_id, need_id=need.id, category=need.category,
                target=need.target, terms=list(terms_by_need.get(need.id, [])),
                priority=need.priority, license_requirements=licenses,
                language=self._language)

            found: list[DiscoveredEvidence] = []
            decisions: list[dict] = []
            for provider in selected:
                if not provider.available():
                    decisions.append(self._decision(provider, available=False, selected=False,
                                                     reason="no disponible (contrato)", results=0))
                    continue
                consulted.add(provider.name)
                start = time.perf_counter()
                try:
                    results = provider.discover(query)
                except Exception:
                    results = []
                elapsed = round((time.perf_counter() - start) * 1000.0, 1)
                timings[provider.name] = round(timings.get(provider.name, 0.0) + elapsed, 1)
                by_provider[provider.name] = by_provider.get(provider.name, 0) + len(results)
                found.extend(results)
                decisions.append(self._decision(
                    provider, available=True, selected=True,
                    reason="seleccionado (disponible, soporta el medio y la licencia)",
                    results=len(results)))
            for provider, reason in discarded:
                decisions.append(self._decision(provider, available=provider.available(),
                                                 selected=False, reason=reason, results=0))

            found.sort(key=lambda e: e.id)
            discovered.extend(found)
            minimum = need.requirement.minimum
            count = len(found)
            state = (DiscoveryState.COVERED if count >= minimum and minimum > 0
                     else DiscoveryState.PARTIAL if count > 0 else DiscoveryState.PENDING)
            needs_cov.append(NeedCoverage(
                need_id=need.id, category=need.category, target=need.target,
                priority=need.priority, minimum=minimum, ideal=need.requirement.ideal,
                discovered=count, state=state,
                candidate_providers=[p.name for p in selected],
                evidence_ids=[e.id for e in found],
                provider_decisions=sorted(decisions, key=lambda d: d["provider"])))

        title = plan.profile.title if plan.profile else ""
        return DiscoveryPlan(
            case_id=plan.case_id, title=title,
            totals=self._totals(needs_cov, discovered),
            by_category=self._by_category(needs_cov),
            by_provider={k: by_provider[k] for k in sorted(by_provider)},
            needs=needs_cov, discovered=sorted(discovered, key=lambda e: e.id),
            sources_consulted=sorted(consulted),
            timings={k: timings[k] for k in sorted(timings)},
            notes=[
                "EAE-004: descubrimiento determinista; NO descarga binarios.",
                "Calidad/licencia/fiabilidad por encima de cantidad; cada evidencia es "
                "autocontenida para la adquisición posterior.",
                "Proveedores sin cliente HTTP actúan como contrato (descubierto=0).",
            ])

    @staticmethod
    def _decision(provider, *, available, selected, reason, results) -> dict:
        return {"provider": provider.name, "available": available, "selected": selected,
                "reason": reason, "results": results, "cost": provider.cost(),
                "reliability": provider.reliability(), "priority": provider.priority()}

    @staticmethod
    def _totals(needs_cov, discovered) -> dict:
        return {
            "required": sum(n.minimum for n in needs_cov),
            "discovered": len(discovered),
            "pending": sum(max(0, n.minimum - n.discovered) for n in needs_cov),
            "needs": len(needs_cov),
            "needs_pending": sum(1 for n in needs_cov if n.state == DiscoveryState.PENDING),
        }

    @staticmethod
    def _by_category(needs_cov: list[NeedCoverage]) -> dict:
        cats: dict[str, dict] = {}
        for n in needs_cov:
            agg = cats.setdefault(n.category, {
                "required": 0, "discovered": 0, "pending": 0, "candidate_providers": []})
            agg["required"] += n.minimum
            agg["discovered"] += n.discovered
            agg["pending"] += max(0, n.minimum - n.discovered)
            for p in n.candidate_providers:
                if p not in agg["candidate_providers"]:
                    agg["candidate_providers"].append(p)
        for agg in cats.values():
            agg["candidate_providers"].sort()
            agg["state"] = (DiscoveryState.COVERED if agg["pending"] == 0 and agg["required"] > 0
                            else DiscoveryState.PARTIAL if agg["discovered"] > 0
                            else DiscoveryState.PENDING)
        return {c: cats[c] for c in sorted(cats)}
