import socket
import os
import threading

class FileServer:
    def __init__(self, host='::1', port=8890, directory='.'):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port, 0, 0))
        self.directory = directory
        
    def start(self):
        self.server.listen(5)
        print(f"Servidor de archivos escuchando en [{self.server.getsockname()[0]}]:{self.server.getsockname()[1]}")
        
        while True:
            client, address = self.server.accept()
            print(f"Nueva conexión de {address}")
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.daemon = True
            thread.start()
    
    def list_files(self):
        return os.listdir(self.directory)
    
    def handle_client(self, client):
        try:
            while True:
                command = client.recv(1024).decode().strip()
                
                if command == "LIST":
                    files = "\n".join(self.list_files())
                    client.sendall(f"FILES:\n{files}".encode())
                
                elif command.startswith("GET "):
                    filename = command[4:]
                    if filename in self.list_files():
                        filepath = os.path.join(self.directory, filename)
                        filesize = os.path.getsize(filepath)
                        client.sendall(f"SIZE {filesize}".encode())
                        
                        with open(filepath, 'rb') as f:
                            while True:
                                chunk = f.read(8192)
                                if not chunk:
                                    break
                                client.sendall(chunk)
                    else:
                        client.sendall(b"ERROR: File not found")
                
                elif command == "QUIT":
                    break
        except:
            pass
        finally:
            client.close()

def get_file(host='::1', port=8890, filename=None):
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        client.connect((host, port, 0, 0))
        
        if not filename:
            client.sendall(b"LIST")
            response = client.recv(4096).decode()
            print(response)
            return
        
        client.sendall(f"GET {filename}".encode())
        response = client.recv(1024).decode()
        
        if response.startswith("SIZE "):
            size = int(response[5:])
            print(f"Descargando {filename} ({size} bytes)")
            
            with open(f"downloaded_{filename}", 'wb') as f:
                received = 0
                while received < size:
                    chunk = client.recv(min(8192, size - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    print(f"Progreso: {(received/size)*100:.1f}%")
            
            print("Descarga completada")
        else:
            print(response)
            
    finally:
        client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = FileServer()
        server.start()
    else:
        filename = sys.argv[1] if len(sys.argv) > 1 else None
        get_file(filename=filename)