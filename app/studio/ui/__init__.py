"""Capa de interfaz de DocumentaryAI Studio (DAS-001).

Importa PySide6 SOLO al arrancar la aplicación (no en import del paquete `app.studio`), para
que los servicios sean testeables sin entorno gráfico. La UI no contiene lógica: delega en
`app.studio.services`.
"""
