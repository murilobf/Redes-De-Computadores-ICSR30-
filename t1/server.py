import socket
import os
import math
import zlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

TAM_BUFFER = 4096
TAM_CABECALHO = 80 
TAM_CONTEUDO = TAM_BUFFER - TAM_CABECALHO

MAX_TENTATIVAS = 3
TIMEOUT_SOCKET = 0.2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))

def checksum_crc32(segmento):
    return zlib.crc32(segmento) & 0xffffffff

def envio(address,num_segmento,conteudo):
    inicio_segmento = num_segmento * TAM_CONTEUDO
    fim_segmento = inicio_segmento + TAM_CONTEUDO
    bloco = conteudo[inicio_segmento:fim_segmento]

    checksum = checksum_crc32(bloco)
    cabecalho = (f"{num_segmento}#{checksum}|").encode("utf-8")
    segmento = cabecalho+bloco

    sock.sendto(segmento, address)
    return segmento

def reenvio(address,num_segmento,conteudo):
    envio(address,num_segmento,conteudo)

print("Servidor iniciado")

while True:
    sock.settimeout(None)
    data,address = sock.recvfrom(TAM_BUFFER)

    mensagem_cliente = data.decode()
    cache_segmentos = []

    if(mensagem_cliente.startswith("ACK")):
        sock.sendto(b"ACK",address)

    elif(mensagem_cliente.startswith("GET")):
        _,nome_arquivo = mensagem_cliente.split(maxsplit=1)

        if not os.path.exists(nome_arquivo):
            sock.sendto(("ERRO|Arquivo não encontrado.").encode("utf-8"), address)
            continue
        else:
            with open(nome_arquivo, "r") as arquivo:
                conteudo = arquivo.read().encode("utf-8")

            qtde_segmentos = math.ceil(len(conteudo)/TAM_CONTEUDO)
            checksum_arquivo = checksum_crc32(conteudo)
            sock.sendto(f"ACK#{qtde_segmentos}#{checksum_arquivo}|Arquivo encontrado. Iniciando transferência".encode("utf-8"), address)

        print(f"Enviando o arquivo {nome_arquivo} para {address} em {qtde_segmentos} arquivos")

        sock.settimeout(TIMEOUT_SOCKET)
        ultimo_recebido = 0   
        qtde_recebidos = 0     

        for num_segmento in range(qtde_segmentos):
            segmento = envio(address, num_segmento, conteudo)
            cache_segmentos.append(segmento)

            tentativas = 0
            while tentativas < MAX_TENTATIVAS:
                try:
                    confirmacao, address = sock.recvfrom(TAM_BUFFER)
                    confirmacao = confirmacao.decode()

                    if confirmacao.startswith("ACK"):
                        ultimo_recebido = int(confirmacao.split("|")[1])
                        break

                except socket.timeout:
                    print(f"Timeout no segmento {num_segmento}. Tentando reenviar...")
                    sock.sendto(cache_segmentos[num_segmento], address)
                    tentativas += 1

            if tentativas == MAX_TENTATIVAS:
                print(f"Falha ao receber confirmação para o segmento {num_segmento} após {MAX_TENTATIVAS} tentativas.")
                break

        sock.sendto(b"FIM",address)
                
    elif(mensagem_cliente.startswith("RESEND /")):
        num_segmento_pedido = mensagem_cliente.split("/")[1]
        print(f"Reenviando o segmento de número {num_segmento_pedido}")

        try:
            sock.sendto(cache_segmentos[num_segmento_pedido], address)
        except:
            sock.sendto("ERRO|segmento não encontrado".encode("utf-8"), address)

    else:
        sock.sendto(("ERRO|Comando inválido").encode("utf-8"), address)
