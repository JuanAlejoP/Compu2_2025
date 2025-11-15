"""
Servidor de Procesamiento Distribuido (Parte B)
Implementa el servidor de procesamiento usando multiprocessing y socketserver.
Procesa tareas computacionalmente intensivas de forma paralela.
"""
import socketserver
import multiprocessing
import struct
import logging
import argparse
import socket
from functools import partial
from multiprocessing import Pool
from common.protocol import parse_message, build_message
from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import generate_thumbnails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool global para procesar tareas CPU-bound
processing_pool = None

def init_pool(num_processes):
    """Inicializa el pool de procesos global"""
    global processing_pool
    processing_pool = Pool(processes=num_processes)
    logger.info(f"Pool de procesos inicializado con {num_processes} workers")

def process_screenshot(url: str) -> str:
    """Genera screenshot de forma segura en un proceso separado"""
    try:
        return generate_screenshot(url)
    except Exception as e:
        logger.error(f"Error generando screenshot para {url}: {e}")
        return None

def process_performance(url: str) -> dict:
    """Analiza rendimiento de forma segura en un proceso separado"""
    try:
        return analyze_performance(url)
    except Exception as e:
        logger.error(f"Error analizando rendimiento para {url}: {e}")
        return {'error': str(e)}

def process_thumbnails(images: list) -> list:
    """Genera thumbnails de forma segura en un proceso separado"""
    try:
        return generate_thumbnails(images)
    except Exception as e:
        logger.error(f"Error generando thumbnails: {e}")
        return []

class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """Handler que procesa solicitudes usando multiprocessing"""
    
    def handle(self):
        """Maneja cada solicitud de cliente"""
        try:
            # Leer la longitud del mensaje (4 bytes big-endian)
            length_bytes = self.request.recv(4)
            if len(length_bytes) < 4:
                logger.warning("No se pudo leer la longitud del mensaje")
                self.request.sendall(b'')
                return
            
            length = struct.unpack('!I', length_bytes)[0]
            
            # Validar que la longitud no sea excesiva (< 10MB)
            if length > 10 * 1024 * 1024:
                logger.error(f"Mensaje demasiado grande: {length} bytes")
                self.request.sendall(b'')
                return
            
            # Leer el payload completo
            data = b''
            while len(data) < length:
                chunk = self.request.recv(min(4096, length - len(data)))
                if not chunk:
                    logger.warning("Conexión cerrada antes de recibir todo el mensaje")
                    return
                data += chunk
            
            logger.info(f"Mensaje recibido: {length} bytes")
            
            # Parsear la solicitud
            request = parse_message(data)
            url = request.get('url')
            images = request.get('images', [])
            
            if not url:
                logger.error("URL faltante en solicitud")
                self.send_error("URL faltante en solicitud")
                return
            
            logger.info(f"Procesando URL: {url} con {len(images)} imágenes")
            
            # Procesar las tareas en paralelo usando el pool
            # Esto es CPU-bound, así que se ejecuta en procesos separados
            global processing_pool
            if processing_pool is None:
                logger.error("Pool no inicializado")
                self.send_error("Error interno: Pool no disponible")
                return
            
            try:
                # Usar apply_async para no bloquear (aunque aquí sí bloqueamos esperando)
                screenshot_result = processing_pool.apply_async(
                    process_screenshot,
                    (url,),
                    callback=lambda x: logger.debug("Screenshot completado"),
                    error_callback=lambda e: logger.error(f"Error en screenshot: {e}")
                )
                
                performance_result = processing_pool.apply_async(
                    process_performance,
                    (url,),
                    callback=lambda x: logger.debug("Performance completado"),
                    error_callback=lambda e: logger.error(f"Error en performance: {e}")
                )
                
                thumbnails_result = processing_pool.apply_async(
                    process_thumbnails,
                    (images,),
                    callback=lambda x: logger.debug("Thumbnails completados"),
                    error_callback=lambda e: logger.error(f"Error en thumbnails: {e}")
                )
                
                # Esperar resultados con timeout
                screenshot = screenshot_result.get(timeout=60)
                performance = performance_result.get(timeout=60)
                thumbnails = thumbnails_result.get(timeout=60)
                
                # Construir respuesta
                response_payload = {
                    'screenshot': screenshot,
                    'performance': performance,
                    'thumbnails': thumbnails
                }
                
                response_json = build_message(response_payload)
                self.request.sendall(response_json)
                
                logger.info(f"Respuesta enviada para {url}")
                
            except Exception as e:
                logger.error(f"Error procesando tareas: {e}")
                self.send_error(f"Error procesando tareas: {str(e)}")
        
        except struct.error as e:
            logger.error(f"Error parsing mensaje: {e}")
            self.send_error(f"Error parsing mensaje: {str(e)}")
        except Exception as e:
            logger.error(f"Error no esperado: {e}")
            self.send_error(f"Error no esperado: {str(e)}")
    
    def send_error(self, error_msg: str):
        """Envía un mensaje de error al cliente"""
        try:
            response = build_message({'error': error_msg})
            self.request.sendall(response)
        except Exception as e:
            logger.error(f"Error enviando error message: {e}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Server que maneja múltiples conexiones con threads"""
    allow_reuse_address = True
    daemon_threads = True

def parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python server_processing.py -i 0.0.0.0 -p 9999 -n 4
  python server_processing.py -i :: -p 9999  (IPv6)
  python server_processing.py --ip localhost --port 9999 --processes 8
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        type=str,
        required=True,
        help='Dirección IP de escucha (ej: 0.0.0.0, ::, localhost)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha (ej: 9999)'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=None,
        help='Número de procesos en el pool (default: CPU count)'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Determinar número de procesos
    num_processes = args.processes if args.processes else multiprocessing.cpu_count()
    
    # Inicializar el pool global
    init_pool(num_processes)
    
    # Crear servidor
    server_address = (args.ip, args.port)
    server = ThreadedTCPServer(server_address, ProcessingRequestHandler)
    
    logger.info(f"Servidor de procesamiento escuchando en {args.ip}:{args.port}")
    logger.info(f"Usando {num_processes} procesos de trabajo")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Cerrando servidor...")
        server.shutdown()
        if processing_pool:
            processing_pool.close()
            processing_pool.join()
        logger.info("Servidor cerrado correctamente")