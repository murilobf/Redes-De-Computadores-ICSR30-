import socket
import threading
import hashlib
import os

TAM_BUFFER = 4096

#TODO: IMPLEMENTAR A VERIFICACAO DO SHA256
def sha256(dado):
    sha = hashlib.sha256()

def broadcast(mensagem):
    
    mensagem_formatada = f'BROADCAST|{mensagem}'.encode()

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

    return formatado


def processar(conexao, endereco):
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
                            sha_arquivo = sha256(conteudo)

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

#Aguarda clientes
while True:
    conexao, endereco = servidor.accept()

    print(f"Criando thread para cliente {endereco}")
    thread_cliente = threading.Thread(target=processar, args=(conexao,endereco))
    thread_cliente.start()