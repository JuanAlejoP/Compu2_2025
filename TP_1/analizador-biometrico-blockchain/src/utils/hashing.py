import hashlib
import json
from typing import Dict, Any


def compute_block_hash(prev_hash: str, datos: Dict[str, Any], timestamp: str) -> str:
    """
    Calcula el hash SHA-256 de un bloque usando:
    - El hash del bloque anterior
    - Los datos del bloque (serializados y ordenados)
    - El timestamp
    Devuelve el hash hexadecimal como string.
    """
    datos_str = json.dumps(datos, sort_keys=True, ensure_ascii=False)
    hash_input = (prev_hash + datos_str + timestamp).encode("utf-8")
    return hashlib.sha256(hash_input).hexdigest()