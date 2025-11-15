"""
Cliente de prueba para TP2
Interactúa con el servidor de scraping para enviar URLs y recibir resultados.
"""

import requests
import json
import argparse
import sys
from urllib.parse import urljoin

def main():
    parser = argparse.ArgumentParser(
        description='Cliente para el servidor de scraping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python client.py -s http://localhost:8081 -u https://example.com
  python client.py --server http://192.168.1.100:8081 --url https://google.com
        """
    )
    
    parser.add_argument(
        '-s', '--server',
        type=str,
        default='http://localhost:8081',
        help='URL del servidor de scraping (default: http://localhost:8081)'
    )
    
    parser.add_argument(
        '-u', '--url',
        type=str,
        help='URL a scrapear'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Archivo con URLs (una por línea)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Guardar resultado en archivo JSON'
    )
    
    args = parser.parse_args()
    
    if not args.url and not args.file:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(1)
        else:
            # Leer URLs de stdin si está redirigido
            urls = [line.strip() for line in sys.stdin if line.strip()]
    elif args.url:
        urls = [args.url]
    else:
        # Leer URLs de archivo
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado: {args.file}", file=sys.stderr)
            sys.exit(1)
    
    results = []
    
    for url in urls:
        try:
            print(f"\n{'='*60}")
            print(f"Scrapeando: {url}")
            print('='*60)
            
            # Construir endpoint
            endpoint = urljoin(args.server, '/scrape')
            
            # Hacer solicitud
            response = requests.get(
                endpoint,
                params={'url': url},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if args.output:
                    results.append(data)
                else:
                    # Mostrar resultado formateado
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Mostrar resumen
                if data.get('status') == 'success':
                    scraping = data.get('scraping_data', {})
                    processing = data.get('processing_data', {})
                    
                    print(f"\n✓ Éxito")
                    print(f"  - Título: {scraping.get('title', 'N/A')}")
                    print(f"  - Links: {len(scraping.get('links', []))}")
                    print(f"  - Imágenes: {scraping.get('images_count', 0)}")
                    print(f"  - Metadatos: {len(scraping.get('meta_tags', {}))}")
                    
                    if processing.get('performance'):
                        perf = processing['performance']
                        print(f"  - Tiempo de carga: {perf.get('load_time_ms', 'N/A')}ms")
                        print(f"  - Tamaño: {perf.get('total_size_kb', 'N/A')}KB")
                    
                    if processing.get('screenshot'):
                        print(f"  - Screenshot: OK ({len(processing['screenshot'])//1024}KB)")
                    
                    if processing.get('thumbnails'):
                        print(f"  - Thumbnails: {len(processing['thumbnails'])}")
                else:
                    print(f"✗ Error: {data.get('error', 'Error desconocido')}")
            else:
                print(f"✗ Error HTTP {response.status_code}: {response.text}")
        
        except requests.Timeout:
            print(f"✗ Timeout: La solicitud tardó demasiado")
        except requests.ConnectionError:
            print(f"✗ Error de conexión: ¿Está el servidor ejecutándose?")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    # Guardar resultados si se especificó archivo de salida
    if args.output and results:
        try:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Resultados guardados en {args.output}")
        except Exception as e:
            print(f"✗ Error guardando archivo: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()