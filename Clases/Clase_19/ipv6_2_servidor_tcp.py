import socket

# Crear socket IPv6
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Configurar para reutilizar la dirección
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enlazar a dirección y puerto
# '::1' es localhost en IPv6
# '::' escucha en todas las interfaces
server_address = ('::1', 8080, 0, 0)  # Los últimos dos ceros son flowinfo y scopeid
server_socket.bind(server_address)

# Escuchar conexiones
server_socket.listen(5)
print(f"Servidor IPv6 escuchando en [{server_address[0]}]:{server_address[1]}")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión desde: {client_address}")
        
        with client_socket:
            # Recibir datos
            data = client_socket.recv(1024)
            print(f"Recibido: {data.decode()}")
            
            # Enviar respuesta
            response = f"Servidor recibió: {data.decode()}"
            client_socket.sendall(response.encode())

except KeyboardInterrupt:
    print("\nServidor detenido.")
finally:
    server_socket.close()