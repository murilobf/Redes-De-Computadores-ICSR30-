import socket
import hashlib
import threading
import queue

TAM_BUFFER = 4096
TEMPO_TIMEOUT = 2

sock_cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

queue_respostas = queue.Queue()

evento_parada = threading.Event()

def calcula_sha256(dado):
    sha = hashlib.sha256()
    sha.update(dado) 
    return sha.hexdigest()

def formata_tamanho(tamanho_bytes):
    sufixos = ['B','kB','MB','GB']

    for sufixo in sufixos:

        if(tamanho_bytes/1024 < 1):
            return (str(round(tamanho_bytes,2)) + sufixo)
            
        tamanho_bytes /= 1024

def recebe(evento_parada):    
    while not evento_parada.is_set():
        try:
            resposta = sock_cliente.recv(TAM_BUFFER)

            if not resposta:
                print("\n Servidor encerrou a conexão. Encerrando programa")
                evento_parada.set()
                break

            if(resposta.startswith(b"BROADCAST") or resposta.startswith(b"CHAT")):
                print(f"\n{resposta.decode()}\n")

            elif(resposta.startswith(b"ERRO")):
                print(f"\n{resposta.decode()}\n")

            else:
                queue_respostas.put(resposta)
        except Exception as e:
            print(f"Conexão com o servidor perdida. Encerrando programa. \n \
                  Exceção: {e}")
            evento_parada.set()

while True:
    endereco = input("Insira o servidor que quer se conectar no formato IP:PORTA (Ex: 127.0.0.1:5005). ").strip()

    try:
        ip,port = endereco.split(":")
        port = int(port)

        try:
            sock_cliente.connect((ip,port))
            thread_recebe = threading.Thread(target=recebe,args=(evento_parada,))
            thread_recebe.start()
            print("\nCONECTADO COM SUCESSO\n")
            break

        except (socket.timeout, OSError):
            print("Erro ao conectar, verifique servidor ou porta inseridos")
            continue

    except ValueError:
        print("Formato inválido, insira no formato IP:PORTA")
        continue

print("====================================\n \
      FAÇA ALGUMA REQUISIÇÃO\n \
      REQUISIÇÕES ACEITAS:\n \
      GET|arquivo.ext\n \
      CHAT|lorem ipsum\n \
      SAIR \n\
====================================")



while not evento_parada.is_set():
    pedido = input("").encode()
    resposta = b''

    sock_cliente.sendall(pedido)
            
    if(pedido.startswith(b'SAIR')):
        evento_parada.set()
        break
    
    elif(pedido.startswith(b'GET|')):
        try:
            resposta = queue_respostas.get(timeout=2) 
        except Exception as e:
            print(e)
            print("Algo deu errado. Tempo de resposta excedido.")


    if(resposta.startswith(b"INICIO")):
        _,metadados = resposta.split(b"|",1)
        metadados,bloco = metadados.split(b"|",1)    
        metadados = metadados.decode()    
        tam_arquivo,hash_arquivo = metadados.split("#",1)
        tam_arquivo = int(tam_arquivo)
        print(metadados)

        caminho_arquivo = pedido.split(b"|",1)[1]
        print(f"INICIANDO ENVIO DO ARQUIVO {caminho_arquivo}. TAMANHO DO ARQUIVO: {formata_tamanho(tam_arquivo)}")

        with open(f"cliente_arquivo_{(caminho_arquivo).decode()}","wb") as arquivo:
            bytes_restantes = tam_arquivo

            if(bloco):
                arquivo.write(bloco)
                bytes_restantes -= len(bloco)

            while bytes_restantes > 0:
                try:
                    bloco = queue_respostas.get(timeout=2)  
                    arquivo.write(bloco)
                    bytes_restantes -= len(bloco)
                except Exception as e:
                    print(f"\nEnvio interrompido.\n \
                          {e}")
                    break

        with open(f"cliente_arquivo_{(caminho_arquivo).decode()}","rb") as arquivo:
            hash_recebido = calcula_sha256(arquivo.read())

        if(hash_recebido == hash_arquivo):
            print("\nArquivo integro. Recebido e salvo com sucesso!\n")

        else:
            print("\nAlgo deu errado, o arquivo foi corrompido. Solicite novamente\n")
                
thread_recebe.join()
print("Desconectado do servidor. Encerrando programa")