import aiohttp
import asyncio
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

async def fetch_html(url: str, timeout: int = 30) -> str:
    """
    Descarga el HTML de una URL de forma asíncrona usando aiohttp.
    
    Args:
        url: URL a descargar
        timeout: Timeout en segundos (default: 30)
    
    Returns:
        Contenido HTML como string
    
    Raises:
        ValueError: Si la URL es inválida
        asyncio.TimeoutError: Si se excede el timeout
        aiohttp.ClientError: Para otros errores de cliente
    """
    # Validar que la URL sea válida
    try:
        parsed = urlparse(url)
        if not parsed.scheme in ('http', 'https'):
            raise ValueError(f"Esquema inválido: {parsed.scheme}. Se requiere http o https")
        if not parsed.netloc:
            raise ValueError(f"URL inválida: sin dominio")
    except Exception as e:
        raise ValueError(f"URL inválida: {str(e)}")
    
    # Configurar timeout
    timeout_config = aiohttp.ClientTimeout(total=timeout)
    
    # Configurar conector con límites
    connector = aiohttp.TCPConnector(
        limit=100,  # Máximo 100 conexiones simultáneas
        limit_per_host=10,  # Máximo 10 por host
        ttl_dns_cache=300,  # Cache DNS por 5 minutos
        enable_cleanup_closed=True
    )
    
    try:
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout_config
        ) as session:
            # Headers estándar
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers, ssl=False) as response:
                # Verificar status code
                if response.status == 404:
                    raise ValueError(f"Página no encontrada (404): {url}")
                elif response.status == 403:
                    raise ValueError(f"Acceso denegado (403): {url}")
                elif response.status >= 400:
                    raise ValueError(f"Error HTTP {response.status}: {url}")
                
                response.raise_for_status()
                
                # Limitar tamaño del contenido (máximo 50MB)
                max_size = 50 * 1024 * 1024
                content = await response.text()
                
                if len(content.encode('utf-8')) > max_size:
                    logger.warning(f"Contenido muy grande ({len(content)} bytes) para {url}")
                
                logger.info(f"HTML descargado exitosamente de {url} ({len(content)} bytes)")
                return content
    
    except asyncio.TimeoutError:
        logger.error(f"Timeout descargando {url}")
        raise asyncio.TimeoutError(f"Timeout descargando {url}")
    except aiohttp.ClientSSLError as e:
        logger.error(f"Error SSL: {e}")
        raise ValueError(f"Error SSL descargando {url}: {str(e)}")
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Error de conexión: {e}")
        raise ValueError(f"Error de conexión con {url}: {str(e)}")
    except aiohttp.ClientError as e:
        logger.error(f"Error de cliente aiohttp: {e}")
        raise ValueError(f"Error descargando {url}: {str(e)}")
    finally:
        await connector.close()
