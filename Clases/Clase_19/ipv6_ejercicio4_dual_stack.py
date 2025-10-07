import socket
import socketserver
import threading
import time
from collections import defaultdict
import json

class Stats:
    def __init__(self):
        self.connections = {'IPv4': 0, 'IPv6': 0}
        self.response_times = []
        self.data_transferred = 0
        self._lock = threading.Lock()
    
    def add_connection(self, is_ipv6):
        with self._lock:
            if is_ipv6:
                self.connections['IPv6'] += 1
            else:
                self.connections['IPv4'] += 1
    
    def add_response_time(self, time_ms):
        with self._lock:
            self.response_times.append(time_ms)
    
    def add_data(self, bytes_count):
        with self._lock:
            self.data_transferred += bytes_count
    
    def get_report(self):
        with self._lock:
            avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            return {
                'connections': dict(self.connections),
                'avg_response_time_ms': round(avg_time, 2),
                'total_data_bytes': self.data_transferred
            }

class DualStackHandler(socketserver.BaseRequestHandler):
    def handle(self):
        is_ipv6 = ':' in self.client_address[0]
        self.server.stats.add_connection(is_ipv6)
        
        start_time = time.time()
        
        try:
            data = self.request.recv(1024)
            self.server.stats.add_data(len(data))
            
            # Simular procesamiento
            time.sleep(0.1)
            
            response = f"Echo: {data.decode()}".encode()
            self.request.sendall(response)
            self.server.stats.add_data(len(response))
            
        except Exception as e:
            print(f"Error handling {self.client_address}: {e}")
        finally:
            end_time = time.time()
            self.server.stats.add_response_time((end_time - start_time) * 1000)

class IPv4Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET
    allow_reuse_address = True

class IPv6Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True

def run_server(server_class, host, port, stats):
    server = server_class((host, port), DualStackHandler)
    server.stats = stats
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

if __name__ == "__main__":
    PORT = 8891
    stats = Stats()
    
    # Iniciar servidores IPv4 e IPv6
    ipv4_server = run_server(IPv4Server, '0.0.0.0', PORT, stats)
    ipv6_server = run_server(IPv6Server, '::', PORT, stats)
    
    print(f"Servidor dual-stack escuchando en puerto {PORT}")
    print("Presiona Ctrl+C para ver el reporte y salir")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nGenerando reporte final...")
        report = stats.get_report()
        print(json.dumps(report, indent=2))
        
        print("\nDeteniendo servidores...")
        ipv4_server.shutdown()
        ipv6_server.shutdown()
        ipv4_server.server_close()
        ipv6_server.server_close()