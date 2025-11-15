from PIL import Image
import requests
import io
import base64
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def generate_thumbnails(image_urls: list, thumbnail_size: tuple = (100, 100)) -> list:
    """
    Genera thumbnails optimizados de las imágenes principales.
    
    Args:
        image_urls: Lista de URLs de imágenes
        thumbnail_size: Tamaño del thumbnail (default: 100x100)
    
    Returns:
        Lista de thumbnails en base64
    """
    thumbnails = []
    
    if not image_urls:
        logger.info("No hay imágenes para procesar")
        return thumbnails
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0'
    })
    
    for url in image_urls[:10]:  # Limitar a 10 primeras imágenes
        try:
            # Validar URL
            parsed = urlparse(url)
            if not parsed.scheme:
                logger.warning(f"URL sin esquema: {url}")
                continue
            
            if not parsed.netloc:
                logger.warning(f"URL sin dominio: {url}")
                continue
            
            # Descargar imagen
            response = session.get(
                url,
                timeout=10,
                verify=False
            )
            
            if response.status_code != 200:
                logger.warning(f"Error descargando imagen {url}: HTTP {response.status_code}")
                continue
            
            # Abrir imagen
            img = Image.open(io.BytesIO(response.content))
            
            # Convertir a RGB si es necesario (para JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Crear thumbnail
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Guardar en buffer
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85, optimize=True)
            
            # Convertir a base64
            thumbnail_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            thumbnails.append(thumbnail_b64)
            
            logger.info(f"Thumbnail generado para {url}")
            
        except requests.Timeout:
            logger.warning(f"Timeout descargando imagen: {url}")
            continue
        except requests.RequestException as e:
            logger.warning(f"Error descargando imagen {url}: {e}")
            continue
        except Image.UnidentifiedImageError:
            logger.warning(f"No es una imagen válida: {url}")
            continue
        except Exception as e:
            logger.warning(f"Error procesando imagen {url}: {e}")
            continue
    
    logger.info(f"Generados {len(thumbnails)} thumbnails de {len(image_urls)} imágenes")
    return thumbnails
