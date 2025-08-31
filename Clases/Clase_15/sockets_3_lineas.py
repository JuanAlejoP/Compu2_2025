import socket
import time

def send_lines(sock, lines):
    for line in lines:
        if not line.endswith("\n"):
            line += "\n"
        sock.sendall(line.encode("utf-8"))

def recv_until_closed(sock):
    # Acumula hasta que el peer cierre; en un protocolo real pararíamos por un token/longitud
    chunks = []
    while True:
        b = sock.recv(1024)
        if not b:  # 0 bytes → peer cerró
            break
        chunks.append(b)
    return b"".join(chunks)

def main():
    HOST, PORT = "127.0.0.1", 9002
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_lines(s, ["Uno", "Dos", "Tres"])  # desde la terminal del `nc` podés escribir respuestas
        time.sleep(10)                         # esperar un poco para que el usuario pueda escribir
        s.shutdown(socket.SHUT_WR)             # anuncias que ya no enviarás más
        data = recv_until_closed(s)
        print(data.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()

# Antes de correr este script, en otra terminal arrancar:
# nc -l 127.0.0.1 9002