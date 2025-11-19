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
while pedido != b"SAIR":
    pedido = input("Faça alguma requisição. \n" \
    "Requisições aceitas: GET|arquivo.ext; CHAT|lorem ipsum; SAIR;").encode()

    sock_cliente.sendall(pedido)
    resposta = sock_cliente.recv(TAM_BUFFER).decode()

    if(resposta.startswith("ERRO") or resposta.startswith("BROADCAST") or resposta.startswith("OK")):
        print(f"\n{resposta}\n")
    
    elif(resposta.startswith("INICIO")):
        print(f"{resposta}\n\n")
        _,metadados = resposta.split("|",1)
        print(metadados)
        metadados,bloco = metadados.split("|",1) #garantia extra que vira só o header
        tam_arquivo,sha_arquivo = metadados.split("#",1)
        tam_arquivo = int(tam_arquivo)

        with open(f"cliente_arquivo","wb") as arquivo:
            bytes_restantes = tam_arquivo

            if(bloco):
                arquivo.write(bloco.encode())
                bytes_restantes -= len(bloco)

            while bytes_restantes > 0:
                bloco = sock_cliente.recv(min(bytes_restantes,TAM_BUFFER))  
                arquivo.write(bloco)
                bytes_restantes -= len(bloco)

            resposta = sock_cliente.recv(TAM_BUFFER).decode()
            print(resposta)
                    

print("Desconectado do servidor. Encerrando programa")