import socket
import time

HOST, PORT = "127.0.0.1", 9004

def try_connect(max_retries=8, base_backoff=1): # segundos entre reintentos
    for attempt in range(1, max_retries + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # segundos
                s.connect((HOST, PORT))
                print("¡Conectado! Esperando respuesta del servidor...") # Mostrar progreso
                s.sendall(b"Ping\n")
                data = s.recv(1024)
                return data
        except (socket.timeout, ConnectionRefusedError) as e:
            sleep_s = base_backoff * attempt
            print(f"Intento {attempt} falló ({e}). Reintento en {sleep_s:.1f}s...")
            time.sleep(sleep_s)
    raise TimeoutError("Servidor no disponible tras varios reintentos")

if __name__ == "__main__":
    print(try_connect())

# Antes de correr este script, en otra terminal arrancar:
# Arrancarlo más tarde para forzar reintentos
# nc -l 127.0.0.1 9004