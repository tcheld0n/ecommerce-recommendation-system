import json
import os
from typing import Dict, Any

DEFAULT_FLAGS: Dict[str, Any] = {
    # Domínios/serviços
    "catalog": True,
    "auth": True,
    "users": True,
    "cart": True,
    "orders": True,
    "payment": True,
    "recommendation": True,
    "shipping": True,
    # Experiências
    "personalizedRecommendations": True,
    "similarInCart": True,
}


class FeatureFlags:
    def __init__(self, file_path: str | None = None) -> None:
        self.file_path = file_path or os.environ.get("FEATURE_FLAGS_FILE", "/app/uploads/features.json")
        self._flags: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._flags = {**DEFAULT_FLAGS, **json.load(f)}
            else:
                self._flags = DEFAULT_FLAGS.copy()
                self.save(self._flags)
        except Exception:
            # Em caso de erro, usar defaults em memória
            self._flags = DEFAULT_FLAGS.copy()

    def save(self, flags: Dict[str, Any]) -> Dict[str, Any]:
        self._flags = {**DEFAULT_FLAGS, **flags}
        # Garantir que o diretório exista. Se dirname for vazio, usar o diretório atual.
        dirpath = os.path.dirname(self.file_path) or "."
        try:
            os.makedirs(dirpath, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._flags, f, ensure_ascii=False, indent=2)
        except Exception:
            # Falha ao persistir em disco: manter em memória e não propagar erro para subir o gateway
            # (logs não podem ser acessados aqui sem depender do logger do gateway)
            pass
        return self._flags

    def get_all(self) -> Dict[str, Any]:
        return self._flags.copy()

    def is_enabled(self, key: str) -> bool:
        return bool(self._flags.get(key, False))
