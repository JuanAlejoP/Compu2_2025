import datetime
import random
import time


def run(frequency_pipe, oxygen_pipe, pressure_pipe):
    # Proceso generador de datos biométricos simulados
    n_samples = 10  # Número de muestras a generar
    print("Iniciando generador...", flush=True)

    try:
        for i in range(n_samples):
            # Generar timestamp actual en formato ISO
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # Crear paquete de datos simulados
            packet = {
                "timestamp": timestamp,
                "frecuencia": random.randint(60, 180),
                "presion": [random.randint(110, 180), random.randint(70, 110)],
                "oxigeno": random.randint(90, 100)
            }

            # Enviar el paquete a cada analizador por su pipe correspondiente
            frequency_pipe.send(packet)
            oxygen_pipe.send(packet)
            pressure_pipe.send(packet)

            print(f"Envío del generador {i+1}/{n_samples} ({timestamp})", flush=True)

            # Esperar 1 segundo antes de la siguiente muestra
            time.sleep(1)

    except KeyboardInterrupt:
        print("Generador interrumpido por usuario", flush=True)

    except Exception as e:
        print(f"Error del generador: {e}", flush=True)

    finally:
        # Enviar señal de fin (None) y cerrar los pipes
        for p in (frequency_pipe, oxygen_pipe, pressure_pipe):
            try:
                p.send(None)
            except Exception:
                pass
            try:
                p.close()
            except Exception:
                pass
        print("El generador terminó y los pipes se cerraron.", flush=True)