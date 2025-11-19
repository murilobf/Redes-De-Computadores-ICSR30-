import socket

TAM_BUFFER = 4096
TEMPO_TIMEOUT = 2

sock_cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock_cliente.settimeout(TEMPO_TIMEOUT)

while True:
    endereco = input("Insira o servidor que quer se conectar no formato IP:PORTA (Ex: 127.0.0.1:5005). ").strip()

    try:
        ip,port = endereco.split(":")
        port = int(port)

        try:
            sock_cliente.connect((ip,port))
            break

        except (socket.timeout, OSError):
            print("Erro ao conectar, verifique servidor ou porta inseridos")
            continue

    except ValueError:
        print("Formato inválido, insira no formato IP:PORTA")
        continue


pedido = ""
while pedido != "SAIR":
    pedido = input("Faça alguma requisição. \n" \
    "Requisições aceitas: GET|arquivo.ext; CHAT|lorem ipsum; SAIR;").encode()

    sock_cliente.sendall(pedido)
    resposta = sock_cliente.recv(TAM_BUFFER).decode()

    if(resposta.startswith("ERRO") or resposta.startswith("BROADCAST") or resposta.startswith("OK")):
        print(f"\n{resposta}\n")
    
    elif(resposta.startswith("INICIO")):
        print(f"{resposta}\n\n")
        _,tam_sha = resposta.split("|")
        tam_arquivo,sha_arquivo = tam_sha.split("#")
        tam_arquivo = int(tam_arquivo)

        while True:
            resposta = sock_cliente.recv(TAM_BUFFER)
            if(resposta.startswith(b"FIM")):
                print(resposta)
                break

            with open(f"cliente_arquivo","ab") as arquivo:
                arquivo.write(resposta)
                    

print("Desconectado do servidor. Encerrando programa")