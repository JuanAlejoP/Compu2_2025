"""
Servidor de Scraping Web Asíncrono (Parte A)
Implementa el servidor principal usando asyncio y aiohttp.
"""

import asyncio
from aiohttp import web
import datetime
import socket
import struct
from scraper.async_http import fetch_html
from scraper.html_parser import parse_html
from scraper.metadata_extractor import extract_metadata
from common.protocol import build_message, parse_message

async def scrape_handler(request):
    url = request.query.get('url')
    if not url:
        return web.json_response({'error': 'Missing url parameter', 'status': 'failed'})
    try:
        html = await fetch_html(url)
        scraping_data = parse_html(html)
        scraping_data['meta_tags'] = extract_metadata(html)
        # Estructura básica y cantidad de imágenes ya están en scraping_data
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        # Comunicación con el servidor de procesamiento
        images = [img for img in scraping_data.get('links', []) if img.endswith(('.jpg', '.png', '.jpeg', '.gif'))]
        req = build_message({'url': url, 'images': images})
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 9999))
            s.sendall(req)
            # Leer primero la longitud
            length_bytes = s.recv(4)
            if len(length_bytes) < 4:
                raise Exception('No se pudo leer la longitud del mensaje')
            length = struct.unpack('!I', length_bytes)[0]
            # Leer el mensaje completo
            data = b''
            while len(data) < length:
                chunk = s.recv(length - len(data))
                if not chunk:
                    break
                data += chunk
        processing_data = parse_message(data)
        response = {
            'url': url,
            'timestamp': timestamp,
            'scraping_data': scraping_data,
            'processing_data': processing_data,
            'status': 'success'
        }
        return web.json_response(response)
    except Exception as e:
        return web.json_response({'error': str(e), 'status': 'failed'})

app = web.Application()
app.add_routes([web.get('/scrape', scrape_handler)])

if __name__ == '__main__':
    web.run_app(app, port=8081)