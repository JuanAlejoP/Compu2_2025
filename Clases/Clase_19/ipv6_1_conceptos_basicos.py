import socket

# IPv4
socket_ipv4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket IPv4 creado")

# IPv6
socket_ipv6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
print("Socket IPv6 creado")

# Cerrar sockets
socket_ipv4.close()
socket_ipv6.close()