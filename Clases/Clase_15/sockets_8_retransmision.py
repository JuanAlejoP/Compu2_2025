import socket

HOST, PORT = "127.0.0.1", 9007

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(1.5) # Tiempo de espera por respuesta
    retries = 7 # Número de reintentos
    for i in range(1, retries + 1):
        try:
            mensaje = f"TIME {i}... ".encode() # Mensaje único cada vez
            s.sendto(mensaje, (HOST, PORT)) # Enviar mensaje
            data, _ = s.recvfrom(2048)
            print("Respuesta:", data.decode())
            break
        except socket.timeout:
            print(f"Timeout intento {i}; reintentando...")
    else:
        print("Sin respuesta tras reintentos")

# Antes de correr este script, en otra terminal arrancar:
# nc -u -l 127.0.0.1 9007