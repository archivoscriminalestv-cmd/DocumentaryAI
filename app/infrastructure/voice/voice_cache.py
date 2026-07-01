"""VoiceCache — caché de audio para minimizar llamadas a ElevenLabs (Sprint C-10).

Clave de caché: sha256(narration + voice_id + model). Si el audio ya existe en
``{base_dir}/audio/{hash}.mp3`` se reutiliza (cache_hit=True) y NO se vuelve a
sintetizar. Si no existe, se sintetiza con el ``SpeechSynthesizer`` inyectado y
se guarda junto a sus metadatos.

Encapsula el detalle de almacenamiento; el núcleo no lo conoce (ARCH-0002 AP-006).
"""

import hashlib
import json
import os
import time


class VoiceCache:
    def __init__(self, synthesizer=None, base_dir: str = "cache") -> None:
        self._synthesizer = synthesizer
        self._audio_dir = os.path.join(base_dir, "audio")
        os.makedirs(self._audio_dir, exist_ok=True)

    @staticmethod
    def key(narration: str, voice_id: str, model: str) -> str:
        raw = f"{narration}\x00{voice_id}\x00{model}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def get_or_synthesize(
        self, *, narration: str, voice_id: str, model: str, scene_id: str
    ) -> tuple[str, bool, bool]:
        """Devuelve (audio_path, cache_hit, synthesized).

        cache_hit=True implica reutilización sin coste de API. En miss, intenta
        sintetizar; ``synthesized`` indica si se obtuvo audio real.
        """
        digest = self.key(narration, voice_id, model)
        path = os.path.join(self._audio_dir, f"{digest}.mp3")

        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path, True, True  # cache hit: nunca se regenera

        synthesized = False
        if self._synthesizer is not None:
            synthesized = self._synthesizer.synthesize(narration, path)
        if synthesized:
            self._write_metadata(digest, voice_id, model, narration, scene_id)
        return path, False, synthesized

    def _write_metadata(
        self, digest: str, voice_id: str, model: str, narration: str, scene_id: str
    ) -> None:
        meta = {
            "hash": digest,
            "voice_id": voice_id,
            "model": model,
            "text_length": len(narration),
            "scene_id": scene_id,
            "timestamp": time.time(),
        }
        meta_path = os.path.join(self._audio_dir, f"{digest}.json")
        try:
            with open(meta_path, "w", encoding="utf-8") as handle:
                json.dump(meta, handle, ensure_ascii=False)
        except OSError:
            pass
