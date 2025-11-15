from bs4 import BeautifulSoup

def extract_metadata(html: str) -> dict:
    """
    Extrae meta tags relevantes (description, keywords, Open Graph).
    """
    soup = BeautifulSoup(html, 'lxml')
    meta_tags = {}
    for tag in soup.find_all('meta'):
        name = tag.get('name') or tag.get('property')
        content = tag.get('content')
        if name and content:
            meta_tags[name] = content
    return meta_tags
