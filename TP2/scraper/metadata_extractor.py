from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_metadata(html: str) -> dict:
    """
    Extrae meta tags relevantes (description, keywords, Open Graph).
    
    Args:
        html: Contenido HTML como string
    
    Returns:
        Dict con metadatos
    """
    meta_tags = {}
    
    if not html or not isinstance(html, str):
        logger.warning("HTML inválido para extraer metadatos")
        return meta_tags
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Meta tags estándar
        standard_names = [
            'description',
            'keywords',
            'author',
            'viewport',
            'charset',
            'robots',
            'language'
        ]
        
        # Open Graph tags
        og_tags = [
            'og:title',
            'og:description',
            'og:image',
            'og:url',
            'og:type',
            'og:site_name'
        ]
        
        # Twitter Card tags
        twitter_tags = [
            'twitter:card',
            'twitter:title',
            'twitter:description',
            'twitter:image'
        ]
        
        all_meta_names = standard_names + og_tags + twitter_tags
        
        for tag in soup.find_all('meta'):
            # Buscar por atributo 'name'
            name = tag.get('name')
            if name and name.lower() in [m.lower() for m in all_meta_names]:
                content = tag.get('content', '').strip()
                if content:
                    meta_tags[name.lower()] = content
            
            # Buscar por atributo 'property' (para Open Graph)
            prop = tag.get('property')
            if prop and prop.lower() in [m.lower() for m in all_meta_names]:
                content = tag.get('content', '').strip()
                if content:
                    meta_tags[prop.lower()] = content
        
        logger.info(f"Metadatos extraídos: {len(meta_tags)} tags")
        return meta_tags
        
    except Exception as e:
        logger.error(f"Error extrayendo metadatos: {e}")
        return meta_tags
