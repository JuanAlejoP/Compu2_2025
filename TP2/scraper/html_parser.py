from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def parse_html(html: str) -> dict:
    """
    Parsea el HTML y extrae título, links, headers, imágenes.
    
    Args:
        html: Contenido HTML como string
    
    Returns:
        Dict con estructura de la página
    """
    if not html or not isinstance(html, str):
        logger.error("HTML inválido")
        return {
            'title': '',
            'links': [],
            'images_count': 0,
            'structure': {f'h{i}': 0 for i in range(1, 7)},
            'error': 'HTML inválido'
        }
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Extraer título
        title = soup.title.string if soup.title else ''
        title = title.strip() if title else ''
        
        # Extraer links absolutos y relativos
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            if href and not href.startswith('#'):  # Ignorar anchors
                links.append(href)
        
        # Contar imágenes
        images_count = len(soup.find_all('img'))
        
        # Contar headers H1-H6
        headers = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
        
        result = {
            'title': title,
            'links': links,
            'images_count': images_count,
            'structure': headers
        }
        
        logger.info(f"HTML parseado: {len(links)} links, {images_count} imágenes, título: '{title}'")
        return result
        
    except Exception as e:
        logger.error(f"Error parseando HTML: {e}")
        return {
            'title': '',
            'links': [],
            'images_count': 0,
            'structure': {f'h{i}': 0 for i in range(1, 7)},
            'error': str(e)
        }
