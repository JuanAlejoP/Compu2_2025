## 👤 Estudiante
**Nombre:** Juan Alejo Patiño
**Carrera:** Ingeniería Informática

# Analizador Biométrico Blockchain

Sistema concurrente de análisis biométrico con cadena de bloques local. Genera datos simulados de una prueba de esfuerzo, los analiza en paralelo y almacena los resultados en una blockchain local para garantizar integridad.

## Arquitectura del proyecto

El sistema está diseñado como una aplicación concurrente basada en procesos, con la siguiente estructura:

- **Generador (proceso principal):**
  - Simula datos biométricos de una prueba de esfuerzo (frecuencia cardíaca, presión arterial, oxígeno en sangre) cada segundo, durante 60 segundos.
  - Envía cada muestra simultáneamente a los tres analizadores usando pipes independientes.

- **Analizadores (3 procesos):**
  - Cada analizador se especializa en una señal: frecuencia, oxígeno o presión.
  - Reciben los datos completos, extraen su señal y mantienen una ventana móvil de las últimas 30 muestras.
  - Calculan en cada iteración la media y la desviación estándar de su señal.
  - Envían los resultados al verificador usando colas (`Queue`).

- **Verificador (proceso):**
  - Espera los resultados de los tres analizadores para cada timestamp.
  - Valida los valores (rango permitido) y marca alertas si corresponde.
  - Construye un bloque con los resultados, el hash del bloque anterior y su propio hash.
  - Encadena y persiste los bloques en un archivo local (`outputs/blockchain.json`).
  - Muestra por pantalla el índice, hash y si hay alerta en cada bloque.

- **Blockchain:**
  - Es una lista enlazada de bloques, donde cada bloque contiene los resultados, hashes y alertas.
  - Garantiza la integridad de los datos mediante el encadenamiento de hashes SHA-256.

- **Script de verificación (`verify_chain.py`):**
  - Permite revisar la integridad de la blockchain, recalculando hashes y verificando el encadenamiento.
  - Genera un reporte estadístico (`outputs/report.txt`) con cantidad de bloques, alertas y promedios.

**Tecnologías y comunicación:**
- Todo el código está en Python 3.9+.
- Se usa el módulo `multiprocessing` para crear procesos y mecanismos de IPC (`Pipe` y `Queue`) para la comunicación.
- No se usan redes ni librerías externas salvo `numpy`.

---


## Requisitos

- Python 3.9 o superior
- `pip` (gestor de paquetes de Python)
- `numpy` (se instala automáticamente con `requirements.txt`)

## Instalación

1. **Clonar el repositorio:**

   ```sh
   git clone https://github.com/JuanAlejoP/Compu2_2025.git
   cd Compu2_2025/TP_1/analizador-biometrico-blockchain
   ```

2. **Instalar las dependencias:**

   ```sh
   pip install -r requirements.txt
   ```

## Ejecución

### 1. Ejecutar el sistema principal

Desde la carpeta `analizador-biometrico-blockchain`, ejecutá:

```sh
python src/main.py
```

Esto iniciará todos los procesos: generador, analizadores y verificador. Se generarán 60 muestras, se analizarán y se almacenarán en `outputs/blockchain.json`.

### 2. Verificar la integridad de la blockchain y generar el reporte

Cuando el sistema principal termine, ejecutá el script de verificación:

```sh
python scripts/verify_chain.py
```

Esto revisará la integridad de la cadena y generará un reporte en `outputs/report.txt`.

## Archivos generados

- `outputs/blockchain.json`: Cadena de bloques con los resultados de cada muestra.
- `outputs/report.txt`: Resumen estadístico y verificación de integridad.


## Pruebas de alertas y bloques corruptos

### Forzar alertas (valores fuera de rango)

Para probar el sistema con alertas, editá el archivo `src/generator/simulator.py` y reemplazá el bloque de creación de `packet` dentro del bucle por:

```python
    # Fuerza valores fuera de rango en las primeras 3 muestras
    if i < 3:
        freq = 220  # fuera de rango
        oxi = 85    # fuera de rango
        pres = [210, 80]  # fuera de rango
    else:
        freq = random.randint(60, 180)
        oxi = random.randint(90, 100)
        pres = [random.randint(110, 180), random.randint(70, 110)]
    packet = {
        "timestamp": timestamp,
        "frecuencia": freq,
        "presion": pres,
        "oxigeno": oxi
    }
```

Para volver al funcionamiento normal, simplemente dejá solo la versión original:

```python
    packet = {
        "timestamp": timestamp,
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno": random.randint(90, 100)
    }
```

### Simular bloques corruptos

1. Ejecutá el sistema normalmente para generar la blockchain.
2. Abrí el archivo `outputs/blockchain.json` con un editor de texto cualquiera.
3. Modificá manualmente el valor de `hash` o `prev_hash` de cualquier bloque (por ejemplo, cambiá un dígito).
4. Guardá el archivo y ejecutá `python scripts/verify_chain.py`.
5. El reporte y la consola indicarán los bloques corruptos detectados.

---

## Notas

- Si por alguna razón se necesita reiniciar el análisis, podés borrar los archivos en `outputs/` antes de ejecutar de nuevo.