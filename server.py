"""
FONTES: 
https://wiki.python.org/moin/UdpCommunication
"""

import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Cria o objeto de tipo socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Envia a mensagem no formato (mensagem (IP, PORT))
sock.sendto(b"hello world", (UDP_IP, UDP_PORT))