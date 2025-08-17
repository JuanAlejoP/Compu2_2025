import json
import os
from typing import List, Dict, Any

# Definir rutas base del proyecto y archivo de blockchain
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(MODULE_DIR, "..", ".."))
BLOCKCHAIN_PATH = os.path.join(PROJECT_ROOT, "outputs", "blockchain.json")

def load_chain(path: str = BLOCKCHAIN_PATH) -> List[Dict[str, Any]]:
    """
    Carga la cadena de bloques desde el archivo especificado.
    Si el archivo no existe o hay error, devuelve una lista vacía.
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
        # Si ocurre un error, devolver lista vacía para no interrumpir el flujo
        return []

def save_chain(chain: List[Dict[str, Any]], path: str = BLOCKCHAIN_PATH) -> None:
    """
    Guarda la cadena de bloques en el archivo especificado en formato JSON.
    Crea el directorio de salida si no existe.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chain, f, indent=2, ensure_ascii=False)