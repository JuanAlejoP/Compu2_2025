import os
import socket

HOST = '127.0.0.1'
PORT = 5000

def manejar_cliente(conn, addr):
    print(f'Nuevo cliente conectado: {addr}')
    conn.sendall(b'Hola, cliente!\n')
    conn.close()
    print(f'Cliente {addr} desconectado.')
    os._exit(0)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f'Servidor escuchando en {HOST}:{PORT}...')

    while True:
        conn, addr = server_socket.accept()
        pid = os.fork()

        if pid == 0:
            server_socket.close()
            manejar_cliente(conn, addr)
        else:
            conn.close()

if __name__ == '__main__':
    main()