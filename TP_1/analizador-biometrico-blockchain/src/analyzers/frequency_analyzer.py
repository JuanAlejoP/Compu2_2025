from collections import deque
import numpy as np


def run(pipe, out_queue):
    """
    Lee paquetes desde pipe, mantiene ventana móvil de 30 muestras sobre 'frecuencia',
    calcula media y desviación y pone resultados en out_queue.
    """
    print("Iniciando analizador de frecuencia...", flush=True)
    window = deque(maxlen=30)

    try:
        while True:
            data = pipe.recv()  # bloqueante
            if data is None:
                break

            value = data.get("frecuencia")
            window.append(value)

            # calcular stats
            media = float(np.mean(window)) if len(window) > 0 else 0.0
            desv = float(np.std(window)) if len(window) > 0 else 0.0

            result = {
                "tipo": "frecuencia",
                "timestamp": data.get("timestamp"),
                "media": media,
                "desv": desv
            }

            out_queue.put(result)
    except EOFError:
        # pipe cerrado de manera abrupta
        pass
    except Exception as e:
        print(f"Frequency analyzer error: {e}", flush=True)
    finally:
        # enviar sentinel para indicar fin al verificador
        try:
            out_queue.put({"tipo": "END"})
        except Exception:
            pass
        print("Analizador de frecuencia finalizado.", flush=True)