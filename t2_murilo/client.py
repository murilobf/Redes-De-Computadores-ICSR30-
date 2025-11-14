import socket

TAM_BUFFER = 4096
TEMPO_TIMEOUT = 2

cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
cliente.settimeout(TEMPO_TIMEOUT)

while True:
    conexao = input("Insira o servidor que quer se conectar no formato IP:PORTA (Ex: 127.0.0.1:5005). ").strip()

    try:
        ip,port = conexao.split(":")
        port = int(port)

        try:
            cliente.connect((ip,port))
            break

        except (socket.timeout, OSError):
            print("Erro ao conectar, verifique servidor ou porta inseridos")
            continue

    except ValueError:
        print("Formato inválido, insira no formato IP:PORTA")
        continue


pedido = ""
while pedido != "SAIR":
    pedido = input()

print("Desconectado do servidor. Encerrando programa")