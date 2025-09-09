import socket

HOST = "127.0.0.1"
PORT = 9101

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"[TCP/IPv4] Escuchando en {HOST}:{PORT} — Ctrl+C para salir")
    try:
        while True:
            conn, addr = srv.accept()
            print("Conexión de", addr)
            with conn:
                buffer = bytearray()
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    buffer.extend(chunk)
                    while True:
                        nl = buffer.find(b"\n")
                        if nl == -1:
                            break
                        line = buffer[:nl]
                        if line.endswith(b"\r"):
                            line = line[:-1]
                        resp = b"eco: " + line + b"\n"
                        conn.sendall(resp)
                        del buffer[:nl+1]
            print("Cierre de", addr)
    except KeyboardInterrupt:
        print("\nServidor detenido")