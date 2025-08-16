from collections import deque
import numpy as np


def run(pipe, out_queue):
    """
    Analizador de presión: usa la componente sistólica (presion[0]) como señal.
    """
    print("Iniciando analizador de presión...", flush=True)
    window = deque(maxlen=30)

    try:
        while True:
            data = pipe.recv()
            if data is None:
                break

            pres = data.get("presion")
            # tomar sistólica (index 0)
            value = pres[0] if pres and len(pres) >= 1 else None
            if value is None:
                continue

            window.append(value)

            media = float(np.mean(window)) if len(window) > 0 else 0.0
            desv = float(np.std(window)) if len(window) > 0 else 0.0

            result = {
                "tipo": "presion",
                "timestamp": data.get("timestamp"),
                "media": media,
                "desv": desv
            }

            out_queue.put(result)
    except EOFError:
        pass
    except Exception as e:
        print(f"Pressure analyzer error: {e}", flush=True)
    finally:
        try:
            out_queue.put({"tipo": "END"})
        except Exception:
            pass
        print("Analizador de presión finalizado.", flush=True)