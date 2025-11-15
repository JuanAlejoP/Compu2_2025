import time
import requests

def analyze_performance(url: str) -> dict:
    start = time.time()
    response = requests.get(url)
    load_time_ms = int((time.time() - start) * 1000)
    total_size_kb = int(len(response.content) / 1024)
    num_requests = 1  # Solo la principal, para simplificar
    return {
        'load_time_ms': load_time_ms,
        'total_size_kb': total_size_kb,
        'num_requests': num_requests
    }
