import socket

HOST, PORT = "0.0.0.0", 9201

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"[UDP/IPv4] {HOST}:{PORT}")
    try:
        while True:
            data, addr = s.recvfrom(4096)
            print(f"{addr} -> {data!r}")
            s.sendto(data, addr)
    except KeyboardInterrupt:
        print("\nServidor UDP detenido")