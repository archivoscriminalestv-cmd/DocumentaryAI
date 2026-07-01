"""Utilidades compartidas por los adapters reales del VPL."""


def constraints_size(request) -> tuple[int, int]:
    c = getattr(request, "provider_constraints", {}) or {}
    return int(c.get("width", 1280)), int(c.get("height", 720))


def with_avoid(prompt: str, negative: str) -> str:
    """Funde negativos en el prompt para proveedores SIN negative_prompt nativo.

    Así el lenguaje cinematográfico (incluidos los negativos) se EJECUTA igualmente
    aunque el proveedor no acepte un campo de negativos separado.
    """
    negative = (negative or "").strip()
    return f"{prompt}. Avoid: {negative}" if negative else prompt


def openai_size(width: int, height: int) -> str:
    """OpenAI gpt-image-1 admite tamaños fijos; mapeamos por orientación."""
    if width > height:
        return "1536x1024"
    if height > width:
        return "1024x1536"
    return "1024x1024"
