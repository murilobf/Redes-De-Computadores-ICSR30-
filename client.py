import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT)) #binda o socket no endereço

while True:
    data,address = sock.recvfrom(1024) # recebe a informação (o 1024 é o tamanho do buffer)

    print(data)