"""
Servidor de Scraping Web Asíncrono (Parte A)
Implementa el servidor principal usando asyncio y aiohttp.
Soporta IPv4 e IPv6 y comunicación asíncrona con el Servidor B.
"""

import asyncio
from aiohttp import web
import datetime
import struct
import logging
import argparse
from scraper.async_http import fetch_html
from scraper.html_parser import parse_html
from scraper.metadata_extractor import extract_metadata
from common.protocol import build_message, parse_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServerConfig:
    """Configuración centralizada del servidor"""
    def __init__(self, host, port, processing_host, processing_port, workers=4):
        self.host = host
        self.port = port
        self.processing_host = processing_host
        self.processing_port = processing_port
        self.workers = workers

async def send_to_processing_server(config: ServerConfig, request_data: dict) -> dict:
    """
    Envía una solicitud al servidor de procesamiento de forma asíncrona.
    Usa asyncio.open_connection en lugar de sockets bloqueantes.
    """
    try:
        reader, writer = await asyncio.open_connection(
            config.processing_host, 
            config.processing_port,
            limit=2**16  # 64KB buffer
        )
        
        # Enviar solicitud
        message = build_message(request_data)
        writer.write(message)
        await writer.drain()
        
        # Leer respuesta: primero la longitud (4 bytes)
        length_bytes = await reader.readexactly(4)
        if len(length_bytes) < 4:
            raise Exception('Error: No se pudo leer la longitud del mensaje')
        
        length = struct.unpack('!I', length_bytes)[0]
        
        # Leer el payload completo
        payload = await reader.readexactly(length)
        
        writer.close()
        await writer.wait_closed()
        
        return parse_message(payload)
        
    except asyncio.TimeoutError:
        logger.error("Timeout al conectar con servidor de procesamiento")
        raise Exception("Timeout: Servidor de procesamiento no responde")
    except ConnectionRefusedError:
        logger.error("Conexión rechazada por servidor de procesamiento")
        raise Exception("Error: Servidor de procesamiento no disponible")
    except Exception as e:
        logger.error(f"Error comunicándose con servidor de procesamiento: {e}")
        raise

async def scrape_handler(request):
    """
    Handler principal que maneja las solicitudes de scraping.
    Coordina automáticamente con el Servidor B.
    """
    url = request.query.get('url')
    if not url:
        return web.json_response(
            {'error': 'Missing url parameter', 'status': 'failed'},
            status=400
        )
    
    try:
        logger.info(f"Iniciando scraping de {url}")
        
        # Paso 1: Descargar HTML de forma asíncrona
        html = await fetch_html(url, timeout=30)
        
        # Paso 2: Parsear HTML localmente
        scraping_data = parse_html(html)
        scraping_data['meta_tags'] = extract_metadata(html)
        
        # Paso 3: Generar timestamp ISO (timezone-aware)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Paso 4: Extraer imágenes para procesamiento
        images = [
            img for img in scraping_data.get('links', []) 
            if img.endswith(('.jpg', '.png', '.jpeg', '.gif', '.webp'))
        ]
        
        # Paso 5: Comunicarse con Servidor B de forma asíncrona
        logger.info(f"Enviando solicitud a servidor de procesamiento")
        processing_data = await send_to_processing_server(
            request.app['config'],
            {'url': url, 'images': images}
        )
        
        # Paso 6: Consolidar respuesta
        response = {
            'url': url,
            'timestamp': timestamp,
            'scraping_data': scraping_data,
            'processing_data': processing_data,
            'status': 'success'
        }
        
        logger.info(f"Scraping completado exitosamente para {url}")
        return web.json_response(response)
        
    except ValueError as e:
        logger.error(f"URL inválida: {e}")
        return web.json_response(
            {'error': f'Invalid URL: {str(e)}', 'status': 'failed'},
            status=400
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout descargando {url}")
        return web.json_response(
            {'error': 'Timeout: La página tardó demasiado en cargar', 'status': 'failed'},
            status=504
        )
    except Exception as e:
        logger.error(f"Error en scraping: {e}")
        return web.json_response(
            {'error': str(e), 'status': 'failed'},
            status=500
        )

async def health_check(request):
    """Endpoint de health check"""
    return web.json_response({'status': 'healthy'})

def create_app(config: ServerConfig) -> web.Application:
    """Factory para crear la aplicación aiohttp"""
    app = web.Application()
    app['config'] = config
    app.add_routes([
        web.get('/scrape', scrape_handler),
        web.get('/health', health_check)
    ])
    return app

def parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python server_scraping.py -i 0.0.0.0 -p 8081 -b localhost -q 9999 -w 4
  python server_scraping.py -i :: -p 8081  (IPv6)
  python server_scraping.py --ip localhost --port 8081 --processing-ip localhost --processing-port 9999
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
        help='Puerto de escucha del servidor (ej: 8081)'
    )
    
    parser.add_argument(
        '-b', '--processing-ip',
        type=str,
        default='localhost',
        help='IP del servidor de procesamiento (default: localhost)'
    )
    
    parser.add_argument(
        '-q', '--processing-port',
        type=int,
        default=9999,
        help='Puerto del servidor de procesamiento (default: 9999)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help='Número de workers (default: 4)'
    )
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    config = ServerConfig(
        host=args.ip,
        port=args.port,
        processing_host=args.processing_ip,
        processing_port=args.processing_port,
        workers=args.workers
    )
    
    app = create_app(config)
    
    logger.info(f"Iniciando servidor en {config.host}:{config.port}")
    logger.info(f"Procesamiento en {config.processing_host}:{config.processing_port}")
    
    web.run_app(app, host=config.host, port=config.port)