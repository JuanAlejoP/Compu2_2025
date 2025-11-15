from bs4 import BeautifulSoup

def parse_html(html: str) -> dict:
    """
    Parsea el HTML y extrae título, links, headers, imágenes.
    """
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string if soup.title else ''
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    images_count = len(soup.find_all('img'))
    headers = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    return {
        'title': title,
        'links': links,
        'images_count': images_count,
        'structure': headers
    }
