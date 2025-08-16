from collections import deque
import numpy as np


def run(pipe, out_queue):
    """
    Analizador de oxígeno: extrae 'oxigeno' y calcula media/desv sobre ventana movil.
    """
    print("Iniciando analizador de oxígeno...", flush=True)
    window = deque(maxlen=30)

    try:
        while True:
            data = pipe.recv()
            if data is None:
                break

            value = data.get("oxigeno")
            window.append(value)

            media = float(np.mean(window)) if len(window) > 0 else 0.0
            desv = float(np.std(window)) if len(window) > 0 else 0.0

            result = {
                "tipo": "oxigeno",
                "timestamp": data.get("timestamp"),
                "media": media,
                "desv": desv
            }

            out_queue.put(result)
    except EOFError:
        pass
    except Exception as e:
        print(f"Oxygen analyzer error: {e}", flush=True)
    finally:
        try:
            out_queue.put({"tipo": "END"})
        except Exception:
            pass
        print("Analizador de oxígeno finalizado.", flush=True)