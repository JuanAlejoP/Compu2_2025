import socket
import threading
import sys

class ChatServer:
    def __init__(self, host='::1', port=8889):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port, 0, 0))
        self.clients = []
        
    def start(self):
        self.server.listen(5)
        print(f"Servidor de chat escuchando en [{self.server.getsockname()[0]}]:{self.server.getsockname()[1]}")
        
        while True:
            client, address = self.server.accept()
            print(f"Nueva conexión de {address}")
            self.clients.append(client)
            
            # Iniciar hilo para manejar al cliente
            thread = threading.Thread(target=self.handle_client, args=(client, address))
            thread.daemon = True
            thread.start()
    
    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.sendall(message)
                except:
                    self.clients.remove(client)
    
    def handle_client(self, client, address):
        try:
            while True:
                message = client.recv(1024)
                if not message:
                    break
                
                # Broadcast del mensaje con la dirección del remitente
                broadcast_msg = f"[{address[0]}]:{address[1]} dice: {message.decode()}".encode()
                self.broadcast(broadcast_msg, client)
                
        except:
            pass
        finally:
            self.clients.remove(client)
            client.close()
            print(f"Cliente {address} desconectado")

class ChatClient:
    def __init__(self, host='::1', port=8889):
        self.client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.client.connect((host, port, 0, 0))
        
    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                print(message)
            except:
                print("Desconectado del servidor")
                break
    
    def send_messages(self):
        while True:
            try:
                message = input()
                if message.lower() == 'quit':
                    break
                self.client.sendall(message.encode())
            except:
                break
        
        self.client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = ChatServer()
        server.start()
    else:
        client = ChatClient()
        receive_thread = threading.Thread(target=client.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        client.send_messages()