import socket
import threading
import hashlib
import os

TAM_BUFFER = 4096

def calcula_sha256(dado):
    sha = hashlib.sha256()
    sha.update(dado) #TODO: PEGAR PARTE POR PARTE (questões de eficiência já que pegar tudo de uma vez só pode pesar um pouco em ambientes multithread)
    return sha.hexdigest()

def broadcast(mensagem):
    
    mensagem_formatada = f'BROADCAST|{mensagem}'.encode()

    with clientes_lock:
        for cliente in clientes_conectados:
            cliente.sendall(mensagem_formatada)#mesma coisa do send mas envia todos os segmentos

def processar_servidor():
    while True:
        mensagem = input("Insira a mensagem a qual deseja realizar o broadcast: ")
        broadcast(mensagem)

def processar_cliente(conexao, endereco):
    with clientes_lock:
        clientes_conectados.append(conexao)

    try:
        while True:
            dado = conexao.recv(TAM_BUFFER)
            
            if not dado:
                print(f"Cliente {endereco} desconectado. Eliminando thread.")
                break

            dado = dado.decode()

            try:
                if dado.startswith("GET|"):
                    _, caminho_arquivo = dado.split("|")

                    if not os.path.exists(caminho_arquivo):
                        msg_erro = f"ERRO 404|Arquivo solicitado nao encontrado. Caminho inserido: {caminho_arquivo}".encode()
                        conexao.sendall(msg_erro)
                        continue

                    else:
                        with open(caminho_arquivo, 'rb') as arquivo:
                            conteudo = arquivo.read()
                            tam_arquivo = (len(conteudo))
                            sha_arquivo = calcula_sha256(conteudo)

                            msg_inicio = f"INICIO|{tam_arquivo}#{sha_arquivo}|".encode()
                            conexao.sendall(msg_inicio)

                            arquivo.seek(0)
                            while True:
                                bloco = arquivo.read(TAM_BUFFER)
                                
                                if not bloco:
                                    break

                                conexao.sendall(bloco)

                            msg_fim = b"FIM|Transferencia finalizada."
                            conexao.sendall(msg_fim)
                        
                elif dado.startswith("CHAT"):
                    _, mensagem = dado.split("|")

                    print(f"MENSAGEM DE [{endereco}]: {mensagem}")
                    msg_ok = b"OK|Mensagem recebida com sucesso!"
                    conexao.sendall(msg_ok)
                    
                elif dado.startswith("SAIR"):
                    print(f"SAIR: CLIENTE {endereco} se desconectou")
                    break

                else:
                    msg_erro = f"ERRO 400|Comando invalido".encode()

                    conexao.sendall(msg_erro)
            except Exception as e:
                print(e)
                msg_erro = f"ERRO 400|Comando invalido".encode()

                conexao.sendall(msg_erro)
            
    finally:
        with clientes_lock:
            clientes_conectados.remove(conexao)
            conexao.close()

#Cria servidor e binda na porta
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("127.0.0.1", 5005))
servidor.listen(0)

clientes_conectados = []
clientes_lock = threading.Lock()

thread_servidor = threading.Thread(target=processar_servidor)
thread_servidor.start()

#Aguarda clientes
while True:
    conexao, endereco = servidor.accept()

    print(f"Criando thread para cliente {endereco}")
    thread_cliente = threading.Thread(target=processar_cliente, args=(conexao,endereco))
    thread_cliente.start()