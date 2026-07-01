"""Gestión de errores centralizada del AIM.

Clasifica cualquier fallo de una API en una categoría objetiva. Los adaptadores NUNCA lanzan
excepciones sin controlar: todo se traduce a un ``AIMError`` con su ``error_class`` y el AIM
decide reintento/fallback. Nunca incluye credenciales ni datos sensibles en el mensaje.
"""


class ErrorClass:
    NONE = "NONE"
    AUTH = "AUTH"
    TIMEOUT = "TIMEOUT"
    QUOTA = "QUOTA"
    RATE_LIMIT = "RATE_LIMIT"
    SERVICE_DOWN = "SERVICE_DOWN"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNAVAILABLE = "UNAVAILABLE"

    # errores por los que merece la pena reintentar (transitorios)
    RETRIABLE = (TIMEOUT, RATE_LIMIT, SERVICE_DOWN, UNAVAILABLE)


class AIMError(Exception):
    def __init__(self, error_class: str, message: str = "") -> None:
        super().__init__(message[:160])
        self.error_class = error_class


def classify(*, status_code: int | None = None, exc: Exception | None = None) -> str:
    if exc is not None:
        name = type(exc).__name__.lower()
        if "timeout" in name:
            return ErrorClass.TIMEOUT
        if any(k in name for k in ("connection", "connect", "dns", "ssl")):
            return ErrorClass.SERVICE_DOWN
        return ErrorClass.SERVICE_DOWN
    if status_code is not None:
        if status_code in (401, 403):
            return ErrorClass.AUTH
        if status_code == 402:
            return ErrorClass.QUOTA
        if status_code == 429:
            return ErrorClass.RATE_LIMIT
        if status_code >= 500:
            return ErrorClass.SERVICE_DOWN
        if status_code >= 400:
            return ErrorClass.INVALID_RESPONSE
    return ErrorClass.NONE


# error_class -> estado de health
def to_health_state(error_class: str) -> str:
    from app.aim.models import HealthState
    return {
        ErrorClass.AUTH: HealthState.AUTH_FAILED,
        ErrorClass.TIMEOUT: HealthState.TIMEOUT,
        ErrorClass.QUOTA: HealthState.QUOTA,
        ErrorClass.RATE_LIMIT: HealthState.RATE_LIMITED,
        ErrorClass.SERVICE_DOWN: HealthState.SERVICE_DOWN,
        ErrorClass.INVALID_RESPONSE: HealthState.INVALID_RESPONSE,
        ErrorClass.UNAVAILABLE: HealthState.UNREACHABLE,
    }.get(error_class, HealthState.UNREACHABLE)
