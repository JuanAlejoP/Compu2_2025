import json
import os
from typing import List, Dict, Any

# base dir del proyecto (dos niveles arriba de este archivo: src/blockchain -> src -> project_root)
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(MODULE_DIR, "..", ".."))
BLOCKCHAIN_PATH = os.path.join(PROJECT_ROOT, "outputs", "blockchain.json")


def load_chain(path: str = BLOCKCHAIN_PATH) -> List[Dict[str, Any]]:
    """
    Carga la cadena desde path si existe, devuelve lista vacía si no.
    """
    try:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        # Si algo falla, devolvemos lista vacía para no romper el verificador
        return []


def save_chain(chain: List[Dict[str, Any]], path: str = BLOCKCHAIN_PATH) -> None:
    """
    Persiste la chain en JSON con indentado legible.
    Se asegura de que el directorio exista.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chain, f, indent=2, ensure_ascii=False)