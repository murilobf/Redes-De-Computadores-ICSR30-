import socket
import threading
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
            mensagem = conexao.recv(TAM_BUFFER)
            
            if not mensagem:
                print(f"Cliente {conexao} desconectado. Eliminando thread.")
                break

            mensagem = mensagem.decode()

            if mensagem.startswith("GET"):
                _, caminho_arquivo = mensagem.split("|")


                if not os.path.exists(caminho_arquivo):
                    msg_erro = f"ERRO|Arquivo solicitado nao encontrado. Caminho inserido: {caminho_arquivo}".encode()
                    conexao.sendall(msg_erro)
                    continue

                else:
                    
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

