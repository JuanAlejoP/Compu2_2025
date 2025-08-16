import hashlib
import json
from typing import Dict, Any


def compute_block_hash(prev_hash: str, datos: Dict[str, Any], timestamp: str) -> str:
    """
    Calcula SHA-256 de prev_hash + json(datos, sort_keys=True) + timestamp.
    Usamos json.dumps(sort_keys=True) para determinismo.
    """
    datos_str = json.dumps(datos, sort_keys=True, ensure_ascii=False)
    hash_input = (prev_hash + datos_str + timestamp).encode("utf-8")
    return hashlib.sha256(hash_input).hexdigest()