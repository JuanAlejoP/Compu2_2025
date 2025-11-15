import time
import aiohttp
import asyncio
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def analyze_performance(url: str) -> dict:
    """
    Analiza el rendimiento de carga de una página.
    
    Args:
        url: URL a analizar
    
    Returns:
        Dict con métricas de rendimiento
    """
    try:
        # Validar URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            logger.error(f"URL inválida: {url}")
            return {
                'error': 'URL inválida',
                'load_time_ms': 0,
                'total_size_kb': 0,
                'num_requests': 0
            }
        
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Configurar reintentos
        session = requests.Session()
        retry = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Medir tiempo de carga
        start = time.time()
        
        response = session.get(
            url,
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0'},
            allow_redirects=True,
            verify=True
        )
        
        load_time_ms = int((time.time() - start) * 1000)
        total_size_kb = len(response.content) / 1024
        
        # Contar headers para estimar número de requests
        # (es una simplificación; idealmente usaríamos un navegador real)
        num_requests = 1  # Al menos la principal
        
        # Intentar contar recursos adicionales desde el HTML
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            # Contar recursos
            css_files = len(soup.find_all('link', rel='stylesheet'))
            js_files = len(soup.find_all('script', src=True))
            img_files = len(soup.find_all('img'))
            num_requests += css_files + js_files + img_files
        except:
            pass
        
        result = {
            'load_time_ms': load_time_ms,
            'total_size_kb': round(total_size_kb, 2),
            'num_requests': num_requests
        }
        
        logger.info(f"Performance analizado para {url}: {load_time_ms}ms, {total_size_kb}KB")
        return result
        
    except requests.Timeout:
        logger.error(f"Timeout analizando performance para {url}")
        return {
            'error': 'Timeout',
            'load_time_ms': 0,
            'total_size_kb': 0,
            'num_requests': 0
        }
    except Exception as e:
        logger.error(f"Error analizando performance para {url}: {e}")
        return {
            'error': str(e),
            'load_time_ms': 0,
            'total_size_kb': 0,
            'num_requests': 0
        }
