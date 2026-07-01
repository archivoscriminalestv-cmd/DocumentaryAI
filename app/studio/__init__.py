"""DocumentaryAI Studio (DAS-001) — el SHELL oficial de escritorio de DocumentaryAI.

Studio es la aplicación de escritorio desde la que se orquestará toda interacción con
DocumentaryAI (la CLI sigue existiendo para automatización y testing). NO contiene lógica de
negocio: solo compone y llama a los motores existentes a través de servicios pequeños.

    Studio (UI)  →  services (LearningService/StatusService)  →  CLI existente  →  motores

Regla de oro: Studio nunca reimplementa un motor ni una CLI; los usa. Toda la lógica sigue
viviendo en los motores. Este paquete (`app.studio.services` + `app.studio.config`) está libre
de Qt para poder testearse sin entorno gráfico; la UI (`app.studio.ui`) importa PySide6 de forma
perezosa.
"""

STUDIO_NAME = "DocumentaryAI Studio"
STUDIO_VERSION = "0.1"
STUDIO_BUILD = "DAS-001"

__all__ = ["STUDIO_NAME", "STUDIO_VERSION", "STUDIO_BUILD"]
