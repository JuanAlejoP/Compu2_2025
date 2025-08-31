import socket
import time

HOST, PORT = "127.0.0.1", 9006

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    for i in range(5):
        mensaje = f"Ping {i+1}: ".encode() # Mensaje único cada vez. encode() convierte str a bytes
        s.sendto(mensaje, (HOST, PORT))
        print(f"> {mensaje!r} enviado") # !r muestra la representación con comillas
        data, addr = s.recvfrom(2048)
        print(f"< {data!r} desde {addr}")
        time.sleep(1) # Espera 1 segundo entre pings

# Antes de correr este script, en otra terminal arrancar:
# nc -u -l 127.0.0.1 9006
# Escribir respuesta manual “pong” cuando el cliente envíe “ping”