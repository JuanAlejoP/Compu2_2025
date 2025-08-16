#!/usr/bin/env python3
"""
Verifica la integridad de outputs/blockchain.json recalculando hashes y prev_hash,
informa bloques corruptos y genera outputs/reporte.txt con resumen estadístico.

(El script asume la estructura del repo donde 'src' contiene los módulos).
"""
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Añadir 'src' al path para poder importar los módulos del proyecto

# Rutas absolutas para asegurar ubicación correcta de outputs y src
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from blockchain.blockchain import load_chain, BLOCKCHAIN_PATH  # type: ignore
from utils.hashing import compute_block_hash  # type: ignore

# Siempre genera el reporte en analizador-biometrico-blockchain/outputs/report.txt
OUTPUT_REPORT = os.path.join(PROJECT_ROOT, "outputs", "report.txt")


def verify_chain(chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recorre la chain y verifica:
      - si prev_hash coincide con el hash del bloque anterior
      - si el hash almacenado coincide con el hash recalculado
    Devuelve una lista de dicts con info sobre bloques corruptos (vacía si no hay).
    """
    corrupt_blocks = []
    expected_prev = "0" * 64

    for idx, block in enumerate(chain):
        ts = block.get("timestamp", "")
        datos = block.get("datos", {})
        stored_prev = block.get("prev_hash", "")
        stored_hash = block.get("hash", "")

        # Verificar prev_hash coincide con el esperado
        if stored_prev != expected_prev:
            corrupt_blocks.append({
                "index": idx,
                "timestamp": ts,
                "reason": f"prev_hash mismatch: expected {expected_prev}, got {stored_prev}"
            })

        # Recalcular hash con la misma función usada en la creación
        recalculated = compute_block_hash(stored_prev, datos, ts)
        if recalculated != stored_hash:
            corrupt_blocks.append({
                "index": idx,
                "timestamp": ts,
                "reason": f"hash mismatch: recalculated {recalculated}, stored {stored_hash}"
            })

        # preparar expected_prev para la siguiente iteración
        expected_prev = stored_hash

    return corrupt_blocks


def compute_report_stats(chain: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula:
      - total_blocks
      - alerts_count
      - average of medias: frecuencia, presion (sistólica), oxigeno
    Retorna dict con esos valores (floats con 2 decimales).
    """
    total = len(chain)
    alerts = 0
    sum_freq = 0.0
    sum_pres = 0.0
    sum_oxy = 0.0

    for b in chain:
        if b.get("alerta"):
            alerts += 1
        datos = b.get("datos", {})
        try:
            sum_freq += float(datos["frecuencia"]["media"])
        except Exception:
            pass
        try:
            sum_pres += float(datos["presion"]["media"])
        except Exception:
            pass
        try:
            sum_oxy += float(datos["oxigeno"]["media"])
        except Exception:
            pass

    avg_freq = (sum_freq / total) if total > 0 else 0.0
    avg_pres = (sum_pres / total) if total > 0 else 0.0
    avg_oxy = (sum_oxy / total) if total > 0 else 0.0

    return {
        "total_blocks": total,
        "alerts_count": alerts,
        "avg_frecuencia": round(avg_freq, 2),
        "avg_presion": round(avg_pres, 2),
        "avg_oxigeno": round(avg_oxy, 2)
    }


def write_report(path: str, stats: Dict[str, Any], corrupts: List[Dict[str, Any]]) -> None:
    """Escribe reporte humano en TXT en path (crea outputs/ si hace falta)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    lines = []
    lines.append(f"Reporte generado: {now}")
    lines.append("")
    lines.append(f"Total de bloques: {stats['total_blocks']}")
    lines.append(f"Bloques con alertas: {stats['alerts_count']}")
    lines.append("")
    lines.append("Promedios (medias almacenadas en bloques):")
    lines.append(f"- Frecuencia promedio: {stats['avg_frecuencia']}")
    lines.append(f"- Presión (sistólica) promedio: {stats['avg_presion']}")
    lines.append(f"- Oxígeno promedio: {stats['avg_oxigeno']}")
    lines.append("")

    if corrupts:
        lines.append("BLOQUES CORRUTOS DETECTADOS:")
        for c in corrupts:
            idx = c.get("index")
            ts = c.get("timestamp")
            reason = c.get("reason")
            lines.append(f"- Bloque {idx} (timestamp={ts}): {reason}")
    else:
        lines.append("No se detectaron bloques corruptos. La cadena es válida.")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    # Cargar cadena (usa BLOCKCHAIN_PATH por defecto)
    chain = load_chain()
    if not chain:
        print("No se encontró blockchain.json o la cadena está vacía.", flush=True)
        return  # Salir si no hay cadena

    print(f"Carga de cadena: {len(chain)} bloques.", flush=True)

    # Verificar integridad
    corrupts = verify_chain(chain)

    # Calcular estadísticas
    stats = compute_report_stats(chain)

    # Escribir reporte
    write_report(OUTPUT_REPORT, stats, corrupts)

    # Mostrar resumen en consola
    print(f"Reporte generado en {OUTPUT_REPORT}")
    if corrupts:
        print("¡ATENCIÓN! Se detectaron bloques corruptos:")
        for c in corrupts:
            print(f"- Bloque {c['index']} (timestamp={c['timestamp']}): {c['reason']}")
    else:
        print("Cadena íntegra: no se detectaron bloques corruptos.")


if __name__ == "__main__":
    main()