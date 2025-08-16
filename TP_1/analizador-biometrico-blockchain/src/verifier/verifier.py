import time
import json
import queue as pyqueue
from typing import Dict, Any

from blockchain.blockchain import load_chain, save_chain
from utils.hashing import compute_block_hash


def run(freq_q, oxy_q, pres_q):
    """
    Verificador completo:
    - Recibe resultados de las 3 queues.
    - Espera 3 resultados por timestamp.
    - Valida condiciones y marca alerta si corresponde.
    - Construye bloque con prev_hash y hash y lo persiste en outputs/blockchain.json
    - Muestra índice, hash y alerta por pantalla.
    """
    print("Iniciando verificador...", flush=True)

    # Cargar cadena existente si hubiera
    chain = load_chain()
    print(f"Loaded chain with {len(chain)} blocks.", flush=True)

    # Buffer para agrupar por timestamp
    buffer: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # Control de sentinels (END) enviados por cada analyzer
    ends_needed = 3
    ends_received = 0

    try:
        while True:
            # Si ya recibimos los 3 ENDs y no hay pendientes en buffer, terminamos
            if ends_received >= ends_needed and not buffer:
                break

            # Intentamos leer de cada queue con timeout corto
            try:
                item = freq_q.get(timeout=0.5)
            except pyqueue.Empty:
                item = None

            if item is not None:
                if isinstance(item, dict) and item.get("tipo") == "END":
                    ends_received += 1
                else:
                    ts = item.get("timestamp")
                    buffer.setdefault(ts, {})
                    buffer[ts]["frecuencia"] = {"media": item["media"], "desv": item["desv"]}

            try:
                item = oxy_q.get(timeout=0.5)
            except pyqueue.Empty:
                item = None

            if item is not None:
                if isinstance(item, dict) and item.get("tipo") == "END":
                    ends_received += 1
                else:
                    ts = item.get("timestamp")
                    buffer.setdefault(ts, {})
                    buffer[ts]["oxigeno"] = {"media": item["media"], "desv": item["desv"]}

            try:
                item = pres_q.get(timeout=0.5)
            except pyqueue.Empty:
                item = None

            if item is not None:
                if isinstance(item, dict) and item.get("tipo") == "END":
                    ends_received += 1
                else:
                    ts = item.get("timestamp")
                    buffer.setdefault(ts, {})
                    buffer[ts]["presion"] = {"media": item["media"], "desv": item["desv"]}

            # Buscar timestamps completos en buffer
            completed = [ts for ts, d in buffer.items() if all(k in d for k in ("frecuencia", "presion", "oxigeno"))]
            for ts in sorted(completed):
                datos = {
                    "frecuencia": buffer[ts]["frecuencia"],
                    "presion": buffer[ts]["presion"],
                    "oxigeno": buffer[ts]["oxigeno"],
                }

                # Validaciones (usar medias)
                alerta = False
                try:
                    if datos["frecuencia"]["media"] >= 200:
                        alerta = True
                    if not (90 <= datos["oxigeno"]["media"] <= 100):
                        alerta = True
                    if datos["presion"]["media"] >= 200:
                        alerta = True
                except Exception:
                    # Si faltan datos por alguna razón, consideramos alerta conservadora
                    alerta = True

                prev_hash = chain[-1]["hash"] if chain else "0" * 64
                block_hash = compute_block_hash(prev_hash, datos, ts)

                block = {
                    "timestamp": ts,
                    "datos": datos,
                    "alerta": alerta,
                    "prev_hash": prev_hash,
                    "hash": block_hash
                }

                chain.append(block)
                # Persistir inmediatamente la cadena actualizada
                save_chain(chain)

                index = len(chain) - 1
                print(f"Block {index} | hash: {block_hash} | alerta: {alerta}", flush=True)

                # Borrar del buffer
                del buffer[ts]

            # Pequeña espera para evitar bucle ocupante si no hubo actividad
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Verificador interrumpido por usuario", flush=True)
    except Exception as e:
        print(f"Verificador error inesperado: {e}", flush=True)

    # Final: imprimir resumen
    total_blocks = len(chain)
    alerts = sum(1 for b in chain if b.get("alerta"))
    print(f"Verificador finalizado. Bloques totales: {total_blocks}, con alertas: {alerts}", flush=True)