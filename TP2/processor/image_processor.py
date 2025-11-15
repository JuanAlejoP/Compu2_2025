from PIL import Image
import requests
import io
import base64

def generate_thumbnails(image_urls: list) -> list:
    thumbnails = []
    for url in image_urls:
        try:
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            img.thumbnail((100, 100))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            thumbnails.append(base64.b64encode(buf.getvalue()).decode('utf-8'))
        except Exception:
            continue
    return thumbnails
