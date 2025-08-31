import socket
import time

def recv_all(sock):
    chunks = []
    while True:
        b = sock.recv(64 * 1024)  # 64 KiB por iteración
        if not b:
            break
        print(f"Recibidos {len(b)} bytes en este bloque") # Mostrar progreso
        chunks.append(b)
        time.sleep(0.1)  # Simular procesamiento lento
    return b"".join(chunks)

def main():
    HOST, PORT = "127.0.0.1", 9003
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data = recv_all(s)
        print(f"Recibidos {len(data)} bytes")

if __name__ == "__main__":
    main()

# Antes de correr este script, en otra terminal arrancar:
# nc -N -l 127.0.0.1 9003 < archivo_grande.bin (archivo_grande.bin puede ser creado con: head -c 5M </dev/urandom > archivo_grande.bin)
# El flag -N hace que nc cierre la conexión tras enviar todo