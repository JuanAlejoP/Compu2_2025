from collections import deque
import numpy as np


def run(pipe, out_queue):
    # Proceso analizador de oxígeno en sangre
    print("Iniciando analizador de oxígeno...", flush=True)
    # Ventana móvil para las últimas 30 muestras
    window = deque(maxlen=30)

    try:
        while True:
            # Recibir datos del pipe (bloqueante)
            data = pipe.recv()
            if data is None:
                break

            # Extraer valor de oxígeno y agregar a la ventana
            value = data.get("oxigeno")
            window.append(value)

            # Calcular media y desviación estándar sobre la ventana
            media = float(np.mean(window)) if len(window) > 0 else 0.0
            desv = float(np.std(window)) if len(window) > 0 else 0.0

            # Preparar resultado para el verificador
            result = {
                "tipo": "oxigeno",
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
        print(f"Error del analizador de oxígeno: {e}", flush=True)
    finally:
        # Enviar mensaje de fin al verificador
        try:
            out_queue.put({"tipo": "END"})
        except Exception:
            pass
        print("Analizador de oxígeno finalizado.", flush=True)