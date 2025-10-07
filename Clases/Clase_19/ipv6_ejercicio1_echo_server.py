import socket

def crear_servidor_echo():
    # Crear socket IPv6
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Enlazar al puerto 8888
    server.bind(('::1', 8888, 0, 0))
    server.listen(5)
    print("Servidor echo IPv6 escuchando en [::1]:8888")
    
    try:
        while True:
            client, address = server.accept()
            print(f"Conexión desde {address}")
            
            with client:
                while True:
                    data = client.recv(1024).strip()
                    if not data:
                        break
                        
                    # Verificar comando QUIT
                    if data.decode().upper() == "QUIT":
                        print(f"Cliente {address} solicitó desconexión")
                        break
                    
                    # Enviar respuesta en mayúsculas
                    response = data.decode().upper().encode()
                    client.sendall(response)
            
            print(f"Conexión cerrada con {address}")
            
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.close()

if __name__ == "__main__":
    crear_servidor_echo()