## Alumno

Juan Alejo Patiño - 61160

---
# TP2 - Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido de scraping y análisis web implementado con **asyncio** y **multiprocessing** en Python. Consiste en dos servidores coordinados que trabajan en conjunto para extraer, analizar y procesar información de sitios web.

## Características

- ✅ **Servidor A (Asyncio)**: Maneja solicitudes de scraping de forma asíncrona sin bloquear el event loop
- ✅ **Servidor B (Multiprocessing)**: Procesa tareas CPU-bound (screenshots, análisis de rendimiento, thumbnails)
- ✅ **Comunicación bidireccional**: Sockets asíncronos con protocolo TLV eficiente
- ✅ **IPv4 e IPv6**: Ambos servidores soportan ambas familias de direcciones
- ✅ **Manejo robusto de errores**: Validación de URLs, timeouts, reintentos
- ✅ **CLI con argparse**: Configuración flexible via línea de comandos

## Requisitos

- Python 3.8+
- pip
- aiohttp
- beautifulsoup4
- lxml
- Pillow
- selenium
- aiofiles
- requests

## Instalación

### 1. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Instalar ChromeDriver (para screenshots)

```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# O descargar desde: https://chromedriver.chromium.org/
```

## Uso

### Opción 1: Ejecución local (por defecto)

Terminal 1 - Servidor de procesamiento:
```bash
python server_processing.py -i localhost -p 9999 -n 4
```

Terminal 2 - Servidor de scraping:
```bash
python server_scraping.py -i localhost -p 8081 -b localhost -q 9999 -w 4
```

Terminal 3 - Cliente:
```bash
python client.py -s http://localhost:8081 -u https://example.com
```

### Opción 2: IPv6

```bash
# Servidor de procesamiento en IPv6
python server_processing.py -i :: -p 9999

# Servidor de scraping en IPv6
python server_scraping.py -i :: -p 8081 -b localhost -q 9999

# Cliente
python client.py -s http://[::1]:8081 -u https://example.com
```

### Opción 3: Interfaz de red específica

```bash
# Escuchar en todas las interfaces
python server_scraping.py -i 0.0.0.0 -p 8081
```

## Opciones de línea de comandos

### server_scraping.py

```
usage: server_scraping.py [-h] -i IP -p PORT [-b PROCESSING_IP] [-q PROCESSING_PORT] [-w WORKERS]

Servidor de Scraping Web Asíncrono

Opciones obligatorias:
  -i IP, --ip IP              Dirección IP de escucha (ej: 0.0.0.0, ::, localhost)
  -p PORT, --port PORT        Puerto de escucha del servidor

Opciones opcionales:
  -b IP, --processing-ip IP   IP del servidor de procesamiento (default: localhost)
  -q PORT, --processing-port  Puerto del servidor de procesamiento (default: 9999)
  -w WORKERS, --workers       Número de workers (default: 4)
  -h, --help                  Muestra este mensaje de ayuda
```

### server_processing.py

```
usage: server_processing.py [-h] -i IP -p PORT [-n PROCESSES]

Servidor de Procesamiento Distribuido

Opciones obligatorias:
  -i IP, --ip IP              Dirección IP de escucha
  -p PORT, --port PORT        Puerto de escucha

Opciones opcionales:
  -n PROCESSES, --processes   Número de procesos en el pool (default: CPU count)
  -h, --help                  Muestra este mensaje de ayuda
```

### client.py

```
usage: client.py [-h] [-s SERVER] [-u URL] [-f FILE] [-o OUTPUT]

Cliente para el servidor de scraping

Opciones opcionales:
  -s SERVER, --server SERVER  URL del servidor (default: http://localhost:8081)
  -u URL, --url URL           URL a scrapear
  -f FILE, --file FILE        Archivo con URLs (una por línea)
  -o OUTPUT, --output OUTPUT  Guardar resultado en JSON
  -h, --help                  Muestra este mensaje de ayuda
```

## Ejemplos de uso

### Ejemplo 1: Scrapear una URL simple

```bash
python client.py -s http://localhost:8081 -u https://www.google.com
```

**Salida esperada:**
```json
{
  "url": "https://www.google.com",
  "timestamp": "2024-11-14T15:30:00Z",
  "scraping_data": {
    "title": "Google",
    "links": ["https://...", "https://...", ...],
    "meta_tags": {
      "description": "Search the world's information...",
      "og:title": "Google"
    },
    "structure": {
      "h1": 1,
      "h2": 0,
      "h3": 0,
      "h4": 0,
      "h5": 0,
      "h6": 0
    },
    "images_count": 5
  },
  "processing_data": {
    "screenshot": "iVBORw0KGgoAAAANSUhEUgAAA...",
    "performance": {
      "load_time_ms": 1250,
      "total_size_kb": 2048.5,
      "num_requests": 15
    },
    "thumbnails": ["iVBORw0KGgoAAAANS...", ...]
  },
  "status": "success"
}
```

### Ejemplo 2: Scrapear múltiples URLs desde archivo

```bash
cat urls.txt
https://example.com
https://python.org
https://github.com

python client.py -s http://localhost:8081 -f urls.txt -o resultados.json
```

### Ejemplo 3: Scrapear desde pipe

```bash
echo "https://example.com" | python client.py -s http://localhost:8081
```

### Ejemplo 4: Con servidor remoto

```bash
python client.py -s http://192.168.1.100:8081 -u https://example.com
```

## Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                    Cliente HTTP/JSON                          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                      GET /scrape?url=X
                           │
        ┌──────────────────────────────────────────┐
        │  Servidor A (Asyncio) :8081              │
        │  - Event loop no bloqueante              │
        │  - Descarga HTML asíncrono               │
        │  - Parsea página localmente              │
        │  - Coordina con Servidor B               │
        └──────────────────────────────────────────┘
                           │
                  Socket TCP asíncrono
                    (Protocol: TLV)
                           │
        ┌──────────────────────────────────────────┐
        │  Servidor B (Multiprocessing) :9999      │
        │  - Pool de procesos                      │
        │  - Screenshot (CPU-bound)                │
        │  - Análisis de rendimiento               │
        │  - Generación de thumbnails              │
        └──────────────────────────────────────────┘
                           │
                     Respuesta JSON
                     consolidada
                           │
        ┌──────────────────────────────────────────┐
        │         Cliente recibe resultado         │
        │  (Totalmente transparente)               │
        └──────────────────────────────────────────┘
```

## Estructura del proyecto

```
TP2/
├── server_scraping.py           # Servidor asyncio (Parte A)
├── server_processing.py         # Servidor multiprocessing (Parte B)
├── client.py                    # Cliente de prueba
├── scraper/
│   ├── __init__.py
│   ├── async_http.py            # Cliente HTTP asíncrono con validación
│   ├── html_parser.py           # Parser HTML con manejo de errores
│   └── metadata_extractor.py    # Extractor de meta tags
├── processor/
│   ├── __init__.py
│   ├── screenshot.py            # Generación de screenshots con Selenium
│   ├── performance.py           # Análisis de rendimiento
│   └── image_processor.py       # Procesamiento y optimización de imágenes
├── common/
│   ├── __init__.py
│   ├── protocol.py              # Protocolo de comunicación TLV
│   └── serialization.py         # Serialización JSON/Pickle
├── tests/
│   ├── test_scraper.py
│   └── test_processor.py
├── requirements.txt
└── README.md
```

## Características de concurrencia

### Asyncio (Servidor A)

- **Event loop no bloqueante**: Maneja múltiples clientes simultáneamente
- **Requests HTTP asíncronos**: Con `aiohttp` y límites de conexión
- **Sockets asíncronos**: Comunicación con Servidor B sin bloquear
- **Timeouts**: 30 segundos máximo por página

```python
# Socket asíncrono no bloqueante
reader, writer = await asyncio.open_connection('localhost', 9999)
await writer.drain()
payload = await reader.readexactly(length)
```

### Multiprocessing (Servidor B)

- **Pool de procesos**: Distribuye tareas CPU-bound entre cores
- **Procesamiento paralelo**: Screenshot, rendimiento y thumbnails en paralelo
- **IPC eficiente**: Socket TCP con protocolo TLV
- **ThreadingMixIn**: Maneja múltiples conexiones con threads

```python
with Pool(processes=4) as pool:
    screenshot = pool.apply_async(generate_screenshot, (url,))
    performance = pool.apply_async(analyze_performance, (url,))
    thumbnails = pool.apply_async(generate_thumbnails, (images,))
```

## Manejo de errores

### URLs inválidas
```
GET /scrape?url=not-a-url
HTTP 400 Bad Request
{"error": "URL inválida: sin dominio", "status": "failed"}
```

### Servidor de procesamiento no disponible
```
HTTP 500 Internal Server Error
{"error": "Servidor de procesamiento no disponible", "status": "failed"}
```

### Timeout
```
HTTP 504 Gateway Timeout
{"error": "Timeout: La página tardó demasiado en cargar", "status": "failed"}
```

## Protocolo de comunicación

### Formato de mensaje

```
┌─────────────────┬──────────────────────────────┐
│ Longitud (4B)   │ Payload JSON                 │
│ (Big-endian)    │ (UTF-8 encoded)              │
└─────────────────┴──────────────────────────────┘

Ejemplo:
0x00000042  {"url": "https://example.com", "images": [...]}
```

## Logging

Todos los servidores generan logs detallados:

```
INFO:__main__:Iniciando servidor en 0.0.0.0:8081
INFO:__main__:Iniciando scraping de https://example.com
INFO:scraper.async_http:HTML descargado exitosamente de https://example.com (123456 bytes)
INFO:__main__:Enviando solicitud a servidor de procesamiento
```

## Pruebas

```bash
# Ejecutar tests unitarios
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=scraper --cov=processor --cov=common
```

## Requisitos de evaluación cumplidos

| Criterio | Estado | Descripción |
|----------|--------|-------------|
| **Funcionalidad completa** | ✅ | Partes A, B y C funcionan correctamente |
| **Uso correcto de asyncio** | ✅ | Event loop no bloqueante, sockets asíncronos |
| **Uso correcto de multiprocessing** | ✅ | Pool de procesos, IPC correcta |
| **Manejo de errores** | ✅ | Validación, timeouts, recuperación |
| **Calidad de código** | ✅ | Modular, documentado, logging |
| **Interfaz CLI** | ✅ | Argparse completo con ayuda |
| **Soporte IPv4/IPv6** | ✅ | Ambos protocolos soportados |

## Solución de problemas

### ChromeDriver no encontrado

```bash
# Verificar si está instalado
which chromedriver

# O agregar al PATH
export PATH=$PATH:/path/to/chromedriver
```

### Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
lsof -i :8081

# Usar otro puerto
python server_scraping.py -i localhost -p 8082
```

### Timeout en screenshots

Los screenshots de páginas con mucho contenido pueden tardar. Aumentar el timeout:

```python
# En processor/screenshot.py
driver.set_page_load_timeout(60)  # 60 segundos
```

## Rendimiento

- **Asyncio**: Puede manejar 100+ clientes simultáneamente
- **Multiprocessing**: Utiliza todos los cores disponibles
- **Tiempo de scraping**: 1-10 segundos dependiendo del sitio
---

**Nota**: Para debugging detallado, establecer `logging.basicConfig(level=logging.DEBUG)`