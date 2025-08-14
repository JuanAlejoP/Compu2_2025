import multiprocessing


def main():
    print("Iniciando análisis...")
    from generator.simulator import run as run_generator
    from analyzers.frequency_analyzer import run as run_frequency
    from analyzers.oxygen_analyzer import run as run_oxygen
    from analyzers.pressure_analyzer import run as run_pressure

    # Crear pipes
    frequency_parent, frequency_child = multiprocessing.Pipe()
    oxygen_parent, oxygen_child = multiprocessing.Pipe()
    pressure_parent, pressure_child = multiprocessing.Pipe()

    # Crear procesos
    generator_proc = multiprocessing.Process(
        target=run_generator,
        args=(frequency_parent, oxygen_parent, pressure_parent)
    )
    frequency_proc = multiprocessing.Process(
        target=run_frequency,
        args=(frequency_child,)
        )
    oxygen_proc = multiprocessing.Process(
        target=run_oxygen,
        args=(oxygen_child,)
        )
    pressure_proc = multiprocessing.Process(
        target=run_pressure,
        args=(pressure_child,)
        )

    # Iniciar procesos
    generator_proc.start()
    frequency_proc.start()
    oxygen_proc.start()
    pressure_proc.start()

    # Esperar que terminen
    generator_proc.join()
    frequency_proc.join()
    oxygen_proc.join()
    pressure_proc.join()


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn") # Recomendado para compatibilidad
    main()