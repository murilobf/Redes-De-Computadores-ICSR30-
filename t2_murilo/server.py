import socket
import threading
import hashlib
import os

TAM_BUFFER = 4096

#TODO: IMPLEMENTAR A VERIFICACAO DO SHA256
def sha256(dado):
    sha = hashlib.sha256()

def broadcast(mensagem):
    
    mensagem_formatada = f'SERVIDOR|{mensagem}'.encode()

    with clientes_lock:
        for cliente in clientes_conectados:
            cliente.sendall(mensagem_formatada)#mesma coisa do send mas envia todos os segmentos

def formata_tamanho(tamanho_bytes):
    sufixos = ['B','kB','MB','GB']

    for sufixo in sufixos:
        formatado = str(tamanho_bytes) + sufixo

        if(tamanho_bytes/1024 < 1):
            break
            
        tamanho_bytes /= 1024

    return round(formatado,2)


def processar(conexao, endereco):
    #asd
    with clientes_lock:
        clientes_conectados.append(conexao)

    try:
        while True:
            dado = conexao.recv(TAM_BUFFER)
            
            if not dado:
                print(f"Cliente {conexao} desconectado. Eliminando thread.")
                break

            dado = dado.decode()

            if dado.startswith("GET"):
                _, caminho_arquivo = dado.split("|")

                if not os.path.exists(caminho_arquivo):
                    msg_erro = f"ERRO 404|Arquivo solicitado nao encontrado. Caminho inserido: {caminho_arquivo}".encode()
                    conexao.sendall(msg_erro)
                    continue

                else:
                    with open(caminho_arquivo, 'r') as arquivo:
                        conteudo = arquivo.read().encode()
                        tam_arquivo = formata_tamanho(len(conteudo))
                        sha_arquivo = sha256(conteudo)

                        ack_inicio = f"INICIO|tamanho: {tam_arquivo}#hash sha256:{sha_arquivo}".encode()
                        conexao.sendall(ack_inicio)

                        conexao.sendall(conteudo) #TODO: tem que mandar 4KB por vez
                    
            elif dado.startswith("CHAT"):
                _, mensagem = dado.split("|")

                print(f"MENSAGEM DE [{endereco}]: {mensagem}")
                
            elif dado.startswith("SAIR"):
                _, mensagem = dado.split("|")

                print(f"SAIR: CLIENTE {endereco} se desconectou")
                break

            else:
                msg_erro = f"ERRO 400|Comando invalido"

                conexao.sendall(msg_erro)
               
    finally:
        with clientes_lock:
            clientes_conectados.remove(conexao)

#Cria servidor e binda na porta
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("127.0.0.1", 5005))
servidor.listen(0)

clientes_conectados = []
clientes_lock = threading.Lock()

#Aguarda clientes
while True:
    print("\nAguardando novo cliente\n")
    conexao, endereco = servidor.accept()

    print(f"Criando thread para cliente {endereco}")
    thread_cliente = threading.Thread(target=processar, args=(conexao,endereco))
    thread_cliente.start()