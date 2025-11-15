"""
Cliente de prueba para TP2
Interactúa con el servidor de scraping para enviar URLs y recibir resultados.
"""

import requests
import json

def main():
    url = input("Ingrese la URL a scrapear: ")
    response = requests.get(f"http://localhost:8081/scrape?url={url}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()