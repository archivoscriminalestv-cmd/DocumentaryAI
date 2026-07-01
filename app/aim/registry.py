"""Registry público de proveedores externos del AIM.

Declarativo (NUNCA hardcodeado dentro de otros motores). Cada proveedor declara su contrato
(``ProviderSpec``). El registro permite listar, filtrar por categoría/capacidad y RESOLVER una
capacidad en una cadena proveedor principal → alternativo (por prioridad), sin ``if`` gigantes.
"""

from app.aim.models import Capability as C
from app.aim.models import Category as Cat
from app.aim.models import ProviderSpec, ProviderStatus
from app.aim.providers import ContractProvider

A, K = ProviderStatus.AVAILABLE, ProviderStatus.CONTRACT


def _specs() -> list[ProviderSpec]:
    return [
        # --- Learning --------------------------------------------------------
        ProviderSpec("youtube", Cat.LEARNING, [C.TRANSCRIPTION, C.DOWNLOAD, C.VIDEO], K,
                     documentation="https://github.com/yt-dlp/yt-dlp", cost="free", priority=10),
        # --- Evidence (APIs públicas sin clave) ------------------------------
        ProviderSpec("wikipedia", Cat.EVIDENCE, [C.EVIDENCE, C.DISCOVERY, C.TIMELINE], A,
                     documentation="https://www.mediawiki.org/wiki/API:Main_page", cost="free", priority=10),
        ProviderSpec("wikidata", Cat.EVIDENCE, [C.EVIDENCE, C.TIMELINE], A,
                     documentation="https://www.wikidata.org/w/api.php", cost="free", priority=10),
        ProviderSpec("wikimedia_commons", Cat.EVIDENCE, [C.EVIDENCE, C.IMAGE], A,
                     documentation="https://commons.wikimedia.org/w/api.php", cost="free", priority=10),
        ProviderSpec("internet_archive", Cat.EVIDENCE, [C.EVIDENCE, C.VIDEO], A,
                     documentation="https://archive.org/help/aboutsearch.htm", cost="free", priority=15),
        ProviderSpec("openstreetmap", Cat.EVIDENCE, [C.MAPS, C.EVIDENCE], A,
                     documentation="https://nominatim.org/release-docs/latest/", cost="free", priority=10),
        ProviderSpec("library_of_congress", Cat.EVIDENCE, [C.EVIDENCE], K,
                     documentation="https://www.loc.gov/apis/", cost="free", priority=12),
        ProviderSpec("national_archives", Cat.EVIDENCE, [C.EVIDENCE], K,
                     documentation="https://www.archives.gov/developer", cost="free", priority=12),
        ProviderSpec("europeana", Cat.EVIDENCE, [C.EVIDENCE], K, requires_api_key=True,
                     api_key_env="EUROPEANA_API_KEY",
                     documentation="https://pro.europeana.eu/page/apis", cost="free", priority=20),
        # --- Generation ------------------------------------------------------
        ProviderSpec("anthropic", Cat.GENERATION, [C.LLM], K, requires_api_key=True,
                     api_key_env="ANTHROPIC_API_KEY", documentation="https://docs.anthropic.com",
                     cost="paid", priority=5, alternative="openai"),
        ProviderSpec("openai", Cat.GENERATION, [C.LLM, C.EMBEDDINGS, C.IMAGE], A,
                     requires_api_key=True, api_key_env="OPENAI_API_KEY",
                     documentation="https://platform.openai.com/docs", cost="paid", priority=10,
                     alternative="anthropic"),
        ProviderSpec("elevenlabs", Cat.GENERATION, [C.VOICE], A, requires_api_key=True,
                     api_key_env="ELEVENLABS_API_KEY", documentation="https://elevenlabs.io/docs",
                     cost="paid", priority=10, alternative="sapi_tts"),
        ProviderSpec("sapi_tts", Cat.GENERATION, [C.VOICE], K,
                     documentation="local Windows SAPI", cost="free", priority=30),
        ProviderSpec("runway", Cat.GENERATION, [C.VIDEO], A, requires_api_key=True,
                     api_key_env="RUNWAY_API_KEY", documentation="https://docs.dev.runwayml.com",
                     cost="paid", priority=10, alternative="replicate"),
        ProviderSpec("stability", Cat.GENERATION, [C.IMAGE], K, requires_api_key=True,
                     api_key_env="STABILITY_API_KEY", documentation="https://platform.stability.ai/docs",
                     cost="paid", priority=20, alternative="openai"),
        ProviderSpec("huggingface", Cat.GENERATION, [C.IMAGE, C.EMBEDDINGS], K, requires_api_key=True,
                     api_key_env="HF_TOKEN", documentation="https://huggingface.co/docs/api-inference",
                     cost="free", priority=30, alternative="stability"),
        ProviderSpec("replicate", Cat.GENERATION, [C.IMAGE, C.VIDEO], A, requires_api_key=True,
                     api_key_env="REPLICATE_API_TOKEN", documentation="https://replicate.com/docs",
                     cost="paid", priority=40),
        ProviderSpec("suno", Cat.GENERATION, [C.MUSIC], K, requires_api_key=True,
                     api_key_env="SUNO_API_KEY", documentation="https://suno.ai", cost="paid", priority=10),
        ProviderSpec("google_vision", Cat.GENERATION, [C.OCR], K, requires_api_key=True,
                     api_key_env="GOOGLE_API_KEY", documentation="https://cloud.google.com/vision/docs",
                     cost="paid", priority=10, alternative="tesseract"),
        ProviderSpec("tesseract", Cat.GENERATION, [C.OCR], K,
                     documentation="https://github.com/tesseract-ocr/tesseract", cost="free", priority=30),
        ProviderSpec("deepl", Cat.GENERATION, [C.TRANSLATION], K, requires_api_key=True,
                     api_key_env="DEEPL_API_KEY", documentation="https://developers.deepl.com",
                     cost="paid", priority=10, alternative="google_translate"),
        ProviderSpec("google_translate", Cat.GENERATION, [C.TRANSLATION], K, requires_api_key=True,
                     api_key_env="GOOGLE_API_KEY", documentation="https://cloud.google.com/translate/docs",
                     cost="paid", priority=20),
    ]


class ProviderRegistry:
    def __init__(self, providers: list | None = None) -> None:
        self._providers: dict[str, ContractProvider] = {}
        for provider in providers or []:
            self.register(provider)

    def register(self, provider: ContractProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> ContractProvider | None:
        return self._providers.get(name)

    def all(self) -> list[ContractProvider]:
        return [self._providers[n] for n in sorted(self._providers)]

    def by_category(self, category: str) -> list[ContractProvider]:
        return [p for p in self.all() if p.spec.category == category]

    def by_capability(self, capability: str) -> list[ContractProvider]:
        matching = [p for p in self._providers.values()
                    if capability in p.spec.capabilities and p.spec.status != ProviderStatus.DISABLED]
        return sorted(matching, key=lambda p: (p.spec.priority, p.spec.name))

    def resolve(self, capability: str) -> list[ContractProvider]:
        """Cadena principal → alternativos para una capacidad (por prioridad)."""
        return self.by_capability(capability)


def _adapter_classes() -> dict:
    from app.aim.adapters.elevenlabs import ElevenLabsAdapter
    from app.aim.adapters.internet_archive import InternetArchiveAdapter
    from app.aim.adapters.openai import OpenAIAdapter
    from app.aim.adapters.openstreetmap import OpenStreetMapAdapter
    from app.aim.adapters.replicate import ReplicateAdapter
    from app.aim.adapters.runway import RunwayAdapter
    from app.aim.adapters.wikidata import WikidataAdapter
    from app.aim.adapters.wikimedia import WikimediaCommonsAdapter
    from app.aim.adapters.wikipedia import WikipediaAdapter
    return {
        "openai": OpenAIAdapter, "elevenlabs": ElevenLabsAdapter, "runway": RunwayAdapter,
        "replicate": ReplicateAdapter, "wikipedia": WikipediaAdapter, "wikidata": WikidataAdapter,
        "wikimedia_commons": WikimediaCommonsAdapter,
        "internet_archive": InternetArchiveAdapter, "openstreetmap": OpenStreetMapAdapter,
    }


def default_registry(secrets, *, http=None, recorder=None, breaker=None, policy=None,
                     sleep=None) -> ProviderRegistry:
    """Construye adaptadores reales para los proveedores con integración; los demás quedan como
    contratos. Comparte recorder/breaker/policy entre adaptadores (métricas y circuito únicos)."""
    import time

    from app.aim.metrics import MetricsRecorder
    from app.aim.retry import CircuitBreaker, RetryPolicy

    recorder = recorder or MetricsRecorder()
    breaker = breaker or CircuitBreaker()
    policy = policy or RetryPolicy()
    sleep = sleep or time.sleep
    adapters = _adapter_classes()

    providers = []
    for spec in _specs():
        cls = adapters.get(spec.name)
        if cls is not None:
            providers.append(cls(spec, secrets, http=http, recorder=recorder, breaker=breaker,
                                 policy=policy, sleep=sleep))
        else:
            providers.append(ContractProvider(spec, secrets))
    registry = ProviderRegistry(providers)
    registry.recorder = recorder
    registry.breaker = breaker
    return registry
