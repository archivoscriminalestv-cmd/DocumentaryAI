"""DiversityPlanner — elige composiciones diferentes de forma DETERMINISTA.

Regla: si el valor base de una dimensión LIBRE ya apareció en los últimos N planos,
se sustituye por la alternativa MENOS usada recientemente (LRU), desempatando por el
orden del catálogo. Sin ``random``. Cada cambio queda justificado.

Dimensiones no libres (según el modo narrativo) y todo el contexto de identidad/escena
se conservan intactos: el SDE nunca improvisa ni rompe continuidad.
"""

import dataclasses

from app.sde.history import ShotHistory
from app.sde.models import CATEGORY, VARIABLE_DIMENSIONS, ShotFingerprint
from app.sde.rules import mode_config
from app.sde.scoring import diversity_against


def _pick_alternative(dim: str, current, recent_values: list, history: ShotHistory,
                      global_index: int):
    """Alternativa determinista: la menos usada recientemente; desempate por catálogo."""
    catalog = CATEGORY[dim]

    def _key(candidate):
        last = history.last_use_index(dim, candidate)
        gap = (global_index - last) if last >= 0 else (global_index + 10_000)  # nunca usado
        return (-gap, catalog.index(candidate))  # maximizar gap, luego orden de catálogo

    # 1) Preferir candidatos que NO estén en la ventana reciente.
    fresh = [c for c in catalog if c != current and c not in recent_values]
    pool = fresh or [c for c in catalog if c != current]
    if not pool:
        return current
    return min(pool, key=_key)


class DiversityPlanner:
    def plan(self, base_fp: ShotFingerprint, mode: str, history: ShotHistory):
        config = mode_config(mode)
        free = set(config["free"])
        window = config["window"]
        global_index = len(history)

        final = dataclasses.replace(base_fp)
        changes: list[dict] = []

        for dim in VARIABLE_DIMENSIONS:
            if dim not in free:
                continue
            recent = history.recent_values(dim, window)
            current = getattr(final, dim)
            if current in recent:  # repetición detectada -> buscar otra solución
                alt = _pick_alternative(dim, current, recent, history, global_index)
                if alt != current:
                    setattr(final, dim, alt)
                    changes.append({
                        "dim": dim, "from": current, "to": alt,
                        "reason": f"'{current}' repetido en los últimos {window} planos; "
                                  f"se elige la alternativa menos usada",
                    })

        recent_fps = [r.fingerprint for r in history.recent(window)]
        score = diversity_against(final, recent_fps)
        return final, changes, score
