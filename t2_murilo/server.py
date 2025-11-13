import socket
import threading
import hashlib
import os

TAM_BUFFER = 4096

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientes_conectados = []
clientes_lock = threading.Lock()

def broadcast(mensagem):
    
    mensagem_formatada = f'SERVIDOR| {mensagem}'.encode()

    with clientes_lock:
        for cliente in clientes_conectados:
            cliente.sendall()#mesma coisa do send mas envia todos os segmentos

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
                addr, caminho_arquivo = dado.split("|")

                if not os.path.exists(caminho_arquivo):
                    msg_erro = f"ERRO 404|Arquivo solicitado nao encontrado. Caminho inserido: {caminho_arquivo}".encode()
                    conexao.sendall(msg_erro)
                    continue

                else:
                    with open(caminho_arquivo, 'r') as arquivo:
                        conteudo = arquivo.read().encode()

                    conexao.sendall(conteudo) #TODO: tem que mandar 4KB por vez

            elif dado.startswith("CHAT"):
                addr, mensagem = dado.split("|")

                print(f"MENSAGEM DE [{addr}]: {mensagem}")
                
            elif dado.startswith("SAIR"):
                addr, mensagem = dado.split("|")

                print(f"SAIR: CLIENTE {addr} se desconectou")
                break

            else:
                msg_erro = f"ERRO 400|Comando invalido"

                conexao.sendall(msg_erro)
               
    finally:
        with clientes_lock:
            clientes_conectados.remove(conexao)

#Aguarda clientes
while True:
    print("\nAguardando novo cliente\n")
    conexao, endereco = servidor.accept()

    print(f"Criando thread para cliente {conexao}")
    thread_cliente = threading.Thread(target=processar, args=(conexao,endereco))
    thread_cliente.start()

