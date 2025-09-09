import socket

HOST, PORT = "127.0.0.1", 9010

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"Escuchando en {HOST}:{PORT} ... Ctrl+C para salir")

    while True:
        conn, addr = srv.accept()
        print("Conexión de", addr)
        with conn:
            while True:
                b = conn.recv(4096)
                if not b:
                    break
                conn.sendall(b)
        print("Cierre de", addr)

# Antes de correr este servidor, correr el cliente:
# nc 127.0.0.1 9010