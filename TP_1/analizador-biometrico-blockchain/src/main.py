import multiprocessing


def main():
    # Importar acá para evitar import side-effects en spawn, por el método de multiprocessing
    from generator.simulator import run as run_generator
    from analyzers.frequency_analyzer import run as run_frequency
    from analyzers.oxygen_analyzer import run as run_oxygen
    from analyzers.pressure_analyzer import run as run_pressure
    from verifier.verifier import run as run_verifier

    print("Iniciando análisis biométrico...", flush=True)

    # Crear pipes
    # El generador usará los extremos 'parent' (escribe)
    # Los analizadores usarán los 'child' (leen)
    frequency_parent, frequency_child = multiprocessing.Pipe()
    oxygen_parent, oxygen_child = multiprocessing.Pipe()
    pressure_parent, pressure_child = multiprocessing.Pipe()

    # Crear colas para comunicar los analizadores con el verificador
    # Estas colas permiten que los analizadores envíen datos al verificador
    frequency_queue = multiprocessing.Queue()
    oxygen_queue = multiprocessing.Queue()
    pressure_queue = multiprocessing.Queue()

    # Crear procesos
    verifier_proc = multiprocessing.Process(
        target=run_verifier,
        args=(frequency_queue, oxygen_queue, pressure_queue),
        name="Verifier"
    )

    # Procesos de análisis
    # Cada uno recibe su extremo 'child' del pipe y su cola correspondiente
    # para enviar datos al verificador

    # Proceso de frecuencia
    frequency_proc = multiprocessing.Process(
        target=run_frequency,
        args=(frequency_child, frequency_queue),
        name="FrequencyAnalyzer"
    )
    # Proceso de oxígeno
    oxygen_proc = multiprocessing.Process(
        target=run_oxygen,
        args=(oxygen_child, oxygen_queue),
        name="OxygenAnalyzer"
    )
    # Proceso de presión
    pressure_proc = multiprocessing.Process(
        target=run_pressure,
        args=(pressure_child, pressure_queue),
        name="PressureAnalyzer"
    )

    # Proceso generador que produce datos biométricos
    # Este proceso escribe en los extremos 'parent' de los pipes
    # y no necesita una cola, ya que no envía datos al verificador.
    generator_proc = multiprocessing.Process(
        target=run_generator,
        args=(frequency_parent, oxygen_parent, pressure_parent),
        name="Generator"
    )

    # Iniciar procesos: verificador primero para que consuma mientras se producen
    verifier_proc.start()
    frequency_proc.start()
    oxygen_proc.start()
    pressure_proc.start()
    generator_proc.start()

    # Esperar a que terminen
    generator_proc.join()
    frequency_proc.join()
    oxygen_proc.join()
    pressure_proc.join()

    # Las analizadores enviarán sentinels a sus queues. Esperar al verificador
    verifier_proc.join()

    # Cerrar/limpiar colas en el proceso padre
    for q in (frequency_queue, oxygen_queue, pressure_queue):
        try:
            q.close()
            q.join_thread()
        except Exception:
            pass

    print("Main finalizado.", flush=True)


if __name__ == "__main__":
    # set_start_method en el guard para compatibilidad
    multiprocessing.set_start_method("spawn")
    main()