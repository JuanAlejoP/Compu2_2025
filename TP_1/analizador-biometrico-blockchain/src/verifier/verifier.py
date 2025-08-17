import time
import queue as pyqueue
from typing import Dict, Any

from blockchain.blockchain import load_chain, save_chain
from utils.hashing import compute_block_hash


def run(freq_q, oxy_q, pres_q):
    
    # Proceso verificador: recibe resultados de los analizadores, valida y construye bloques
    print("Iniciando verificador...", flush=True)

    # Cargar la cadena existente (si hay)
    chain = load_chain()
    print(f"Se encontró y cargó una cadena con {len(chain)} bloques.", flush=True)

    # Buffer para agrupar resultados por timestamp
    buffer: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # Control de finalización de los analizadores
    ends_needed = 3
    ends_received = 0

    try:
        while True:
            # Terminar si recibimos todos los END y el buffer está vacío
            if ends_received >= ends_needed and not buffer:
                break

            # Leer de la queue de frecuencia
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

            # Leer de la queue de oxígeno
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

            # Leer de la queue de presión
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

            # Buscar timestamps completos (con los 3 resultados)
            completed = [ts for ts, d in buffer.items() if all(k in d for k in ("frecuencia", "presion", "oxigeno"))]
            for ts in sorted(completed):
                # Construir datos del bloque
                datos = {
                    "frecuencia": buffer[ts]["frecuencia"],
                    "presion": buffer[ts]["presion"],
                    "oxigeno": buffer[ts]["oxigeno"],
                }

                # Validar condiciones de alerta
                alerta = False
                try:
                    if datos["frecuencia"]["media"] >= 200:
                        alerta = True
                    if not (90 <= datos["oxigeno"]["media"] <= 100):
                        alerta = True
                    if datos["presion"]["media"] >= 200:
                        alerta = True
                except Exception:
                    alerta = True

                # Calcular hashes y construir bloque
                prev_hash = chain[-1]["hash"] if chain else "0" * 64
                block_hash = compute_block_hash(prev_hash, datos, ts)

                block = {
                    "timestamp": ts,
                    "datos": datos,
                    "alerta": alerta,
                    "prev_hash": prev_hash,
                    "hash": block_hash
                }

                # Guardar bloque en la cadena y persistir
                chain.append(block)
                save_chain(chain)

                index = len(chain) - 1
                print(f"Block {index} | hash: {block_hash} | alerta: {alerta}", flush=True)

                # Eliminar del buffer
                del buffer[ts]

            # Pequeña espera para evitar bucle ocupado
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Verificador interrumpido por usuario", flush=True)
    except Exception as e:
        print(f"Error inesperado del verificador: {e}", flush=True)

    # Resumen final
    total_blocks = len(chain)
    alerts = sum(1 for b in chain if b.get("alerta"))
    print(f"Verificador finalizado. Bloques totales: {total_blocks}, con alertas: {alerts}", flush=True)