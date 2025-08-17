
from collections import deque
import numpy as np

def run(pipe, out_queue):
    # Proceso analizador de frecuencia cardíaca
    print("Iniciando analizador de frecuencia...", flush=True)
    # Ventana móvil para las últimas 30 muestras
    window = deque(maxlen=30)

    try:
        while True:
            # Recibir datos del pipe (bloqueante)
            data = pipe.recv()
            if data is None:
                break

            # Extraer valor de frecuencia y agregar a la ventana
            value = data.get("frecuencia")
            window.append(value)

            # Calcular media y desviación estándar sobre la ventana
            media = float(np.mean(window)) if len(window) > 0 else 0.0
            desv = float(np.std(window)) if len(window) > 0 else 0.0

            # Preparar resultado para el verificador
            result = {
                "tipo": "frecuencia",
                "timestamp": data.get("timestamp"),
                "media": media,
                "desv": desv
            }

            # Enviar resultado por la queue
            out_queue.put(result)
    except EOFError:
        # Pipe cerrado abruptamente
        pass
    except Exception as e:
        print(f"Error del analizador de frecuencia: {e}", flush=True)
    finally:
        # Enviar mensaje de fin al verificador
        try:
            out_queue.put({"tipo": "END"})
        except Exception:
            pass
        print("Analizador de frecuencia finalizado.", flush=True)