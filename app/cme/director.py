"""NarrativeMotionDirector — decide el movimiento base por INTENCIÓN narrativa.

El movimiento nunca es aleatorio ni Ken Burns por defecto: responde al rol del plano
y al estilo del documental, y se justifica. El planner afinará después (continuidad +
diversidad). Determinista.
"""

# motion_hint del VSC/SDE -> tipo del catálogo CME (prior si la narrativa no manda).
_HINT_TO_MOTION = {
    "slow_push_in": "SLOW_PUSH_IN", "slow_zoom": "SLOW_PUSH_IN", "push_in": "SLOW_PUSH_IN",
    "slow_pull_out": "SLOW_PULL_OUT", "pull_out": "SLOW_PULL_OUT",
    "locked": "LOCKED", "static": "STATIC",
    "parallax": "PARALLAX",
    "tracking_left": "TRUCK_LEFT", "tracking_right": "TRUCK_RIGHT",
    "aerial_descent": "DRONE_REVEAL", "drone": "DRONE_REVEAL",
    "orbit": "ORBIT_RIGHT", "orbital": "ORBIT_RIGHT",
    "ken_burns_drift": "FLOATING", "ken_burns": "FLOATING",
    "pan_left": "PAN_LEFT", "pan_right": "PAN_RIGHT",
}

# Estilo narrativo -> (motion, propósito).
_STYLE_TO_MOTION = {
    "interview": ("SLOW_PUSH_IN", "acercarse lentamente al entrevistado"),
    "testimony": ("MICRO_BREATHING", "testimonio: cámara fija con micro-respiración"),
    "crime": ("DOLLY_RIGHT", "recorrer el lugar de los hechos con un dolly lento"),
    "reconstruction": ("HANDHELD_SUBTLE", "reconstrucción: cámara en mano para inmediatez"),
    "historic": ("PARALLAX", "fotografía histórica: paralaje 2.5D"),
    "intimate": ("SLOW_PUSH_IN", "plano emocional: push-in lento"),
    "reflective": ("SLOW_PULL_OUT", "tono reflexivo: alejarse lentamente"),
    "observational": ("FLOATING", "observación: deriva flotante suave"),
}

# Rol del plano -> (motion, propósito). Tiene prioridad sobre el estilo.
_ROLE_TO_MOTION = {
    "establishing": ("REVEAL", "establecer el espacio con una revelación"),
    "landscape": ("DRONE_REVEAL", "revelar el paisaje desde el aire"),
    "detail": ("MACRO_SLIDE", "explorar el detalle del objeto"),
    "insert": ("MACRO_SLIDE", "inserto de objeto en detalle"),
    "object": ("MACRO_SLIDE", "explorar el objeto en detalle"),
    "transition": ("STATIC", "plano de transición sin movimiento"),
}


class NarrativeMotionDirector:
    def scene_class(self, documentary_style: str) -> str:
        s = (documentary_style or "").lower()
        if any(k in s for k in ("reconstruction", "chase", "action", "persecu", "handheld", "nervous")):
            return "handheld"
        return "steady"

    def base_motion(self, documentary_style: str, shot_role: str, motion_hint: str) -> tuple[str, str]:
        role = (shot_role or "").lower()
        style = (documentary_style or "").lower()

        if role in _ROLE_TO_MOTION:
            return _ROLE_TO_MOTION[role]
        for key, value in _STYLE_TO_MOTION.items():
            if key in style:
                return value
        hint = (motion_hint or "").lower()
        if hint in _HINT_TO_MOTION:
            return _HINT_TO_MOTION[hint], f"sugerencia de cámara del plano ({hint})"
        return "SLOW_PUSH_IN", "movimiento por defecto: push-in lento de intención emocional"
