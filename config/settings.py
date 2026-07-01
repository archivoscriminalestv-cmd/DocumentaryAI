PROJECT_NAME: str = "Fago"

# Selección de proveedor de IA del Narrative Engine (Sprint B-06.1). Cambiar de
# proveedor/modelo se hace SOLO aquí; el resto del sistema depende del puerto
# LLMProvider y del factory create_llm_provider().
AI_PROVIDER: str = "anthropic"  # anthropic | openai | gemini
AI_MODEL: str = "claude-opus-4-8"
