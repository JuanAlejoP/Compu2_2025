"""
Servidor de Procesamiento Distribuido (Parte B)
Implementa el servidor de procesamiento usando multiprocessing y socketserver.
"""
import socketserver
import multiprocessing
import struct
from common.protocol import parse_message, build_message
from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import generate_thumbnails

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Leer primero la longitud del mensaje
        length_bytes = self.request.recv(4)
        if len(length_bytes) < 4:
            self.request.sendall(b'')
            return
        length = struct.unpack('!I', length_bytes)[0]
        data = b''
        while len(data) < length:
            chunk = self.request.recv(length - len(data))
            if not chunk:
                break
            data += chunk
        request = parse_message(data)
        url = request.get('url')
        images = request.get('images', [])
        screenshot = generate_screenshot(url)
        performance = analyze_performance(url)
        thumbnails = generate_thumbnails(images)
        response_payload = {
            'screenshot': screenshot,
            'performance': performance,
            'thumbnails': thumbnails
        }
        response_json = build_message(response_payload)
        self.request.sendall(response_json)

def start_server(host, port):
    with socketserver.TCPServer((host, port), RequestHandler) as server:
        print(f"Server started at {host}:{port}")
        server.serve_forever()

if __name__ == "__main__":
    host, port = "localhost", 9999
    server_process = multiprocessing.Process(target=start_server, args=(host, port))
    server_process.start()
    print(f"Server process started with PID: {server_process.pid}")