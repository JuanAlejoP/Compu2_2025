#!/usr/bin/env python3

# Script para verificar la integridad de la blockchain y generar un reporte estadístico
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Determinar rutas absolutas para importar módulos del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Importar funciones para cargar la cadena y calcular hashes
from blockchain.blockchain import load_chain, BLOCKCHAIN_PATH  # type: ignore
from utils.hashing import compute_block_hash  # type: ignore

# Ruta de salida para el reporte
OUTPUT_REPORT = os.path.join(PROJECT_ROOT, "outputs", "report.txt")


def verify_chain(chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recorre la cadena y verifica:
      - Que prev_hash coincida con el hash del bloque anterior
      - Que el hash almacenado coincida con el hash recalculado
    Devuelve una lista de dicts con información sobre bloques corruptos (vacía si no hay).
    """
    corrupt_blocks = []
    expected_prev = "0" * 64  # Hash inicial para el primer bloque

    for idx, block in enumerate(chain):
        ts = block.get("timestamp", "")
        datos = block.get("datos", {})
        stored_prev = block.get("prev_hash", "")
        stored_hash = block.get("hash", "")

        # Verificar que prev_hash coincida con el esperado
        if stored_prev != expected_prev:
            corrupt_blocks.append({
                "index": idx,
                "timestamp": ts,
                "reason": f"prev_hash mismatch: expected {expected_prev}, got {stored_prev}"
            })

        # Recalcular el hash y comparar
        recalculated = compute_block_hash(stored_prev, datos, ts)
        if recalculated != stored_hash:
            corrupt_blocks.append({
                "index": idx,
                "timestamp": ts,
                "reason": f"hash mismatch: recalculated {recalculated}, stored {stored_hash}"
            })

        expected_prev = stored_hash

    return corrupt_blocks

def compute_report_stats(chain: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Calcula estadísticas globales de la cadena para el reporte
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
    # Escribe el reporte final en un archivo de texto
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
        lines.append("BLOQUES CORRUPTOS DETECTADOS:")
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
    # Punto de entrada principal del script de verificación y reporte
    chain = load_chain()
    if not chain:
        print("No se encontró blockchain.json o la cadena está vacía.", flush=True)
        return

    print(f"Carga de cadena: {len(chain)} bloques.", flush=True)

    corrupts = verify_chain(chain)

    stats = compute_report_stats(chain)

    write_report(OUTPUT_REPORT, stats, corrupts)

    print(f"Reporte generado en {OUTPUT_REPORT}")
    if corrupts:
        print("¡ATENCIÓN! Se detectaron bloques corruptos:")
        for c in corrupts:
            print(f"- Bloque {c['index']} (timestamp={c['timestamp']}): {c['reason']}")
    else:
        print("Cadena íntegra: no se detectaron bloques corruptos.")


if __name__ == "__main__":
    main()