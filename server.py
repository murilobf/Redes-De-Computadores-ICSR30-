"""
FONTES: 
https://wiki.python.org/moin/UdpCommunication
"""

"""
Requisitos do Servidor UDP:

    Inicialização: O servidor deve ser executado antes do cliente.
    FEITO Porta: Deve operar em uma porta UDP especificada, com número maior que 1024 (portas abaixo de 1024 geralmente exigem privilégios de administrador).
    Recepção e Protocolo:
    FEITO    Aguardar conexões/mensagens de clientes.
    FEITO    Interpretar as requisições recebidas. É necessário definir e implementar um protocolo de aplicação simples sobre UDP para que o cliente requisite arquivos (Exemplo de formato de requisição: GET /nome_do_arquivo.ext).
    Processamento da Requisição:
    FEITO    Verificar se o arquivo solicitado existe.
    FEITO       Se o arquivo não existir: Enviar uma mensagem de erro claramente definida pelo seu protocolo para o cliente.
    Transmissão do Arquivo (se existir):
    FEITO    Segmentação: Dividir o arquivo em múltiplos segmentos/pedaços para envio em datagramas UDP.
    FEITO    Cabeçalho Customizado: Cada segmento enviado deve conter informações de controle definidas pelo seu protocolo (ver “Considerações de Protocolo” abaixo).
    TODO    Retransmissão: Implementar lógica para reenviar segmentos específicos caso o cliente solicite (devido a perdas ou erros).


"""

import socket
import os
import math
import zlib
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

TAM_BUFFER = 4096
TAM_CABECALHO = 80 
TAM_CONTEUDO = TAM_BUFFER - TAM_CABECALHO

TIMEOUT_SOCKET = 1
#80 pois foi verificado que, dependendo da quantidade de caracteres (seja pela quantidade de segmentos ou pelo tamanho do checksum)
#o cabeçalho pesava cerca de 60 bytes (casos maiores, fora do escopo do trabalho, mas para garantir ficou assim). Foi deixado mais alguns para margem de segurança.

# Cria o objeto de tipo socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #AF_INET = ipv4 e SOCK_DGRAM = UDP
sock.bind((UDP_IP,UDP_PORT)) #O servidor fica ouvindo nessa porta

def checksum_crc32(segmento):
    return zlib.crc32(segmento) & 0xffffffff

#Função para solicitar o envio ou o reenvio de um segmento perdido/corrompido
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
    


#Envia a mensagem no formato (mensagem (IP, PORT))só pra ter como base
#sock.sendto(b"hello world", (UDP_IP, UDP_PORT))

#Loop pra manter a conexão
while True:
    sock.settimeout(None)
    data,address = sock.recvfrom(TAM_BUFFER) #Espera um novo cliente

    mensagem_cliente = data.decode()

    #Para caso precise reenviar 
    cache_segmentos = []

    #Mensagem simples para verificar conexão
    if(mensagem_cliente.startswith("ACK")):
        sock.sendto(b"ACK",address)

    elif(mensagem_cliente.startswith("GET")):
        _,nome_arquivo = mensagem_cliente.split(maxsplit=1) #O maxsplit é mais pra garantir que não haja espaços em branco

        #Envia mensagem de erro caso o arquivo não exista
        if not os.path.exists(nome_arquivo):
            sock.sendto(("ERRO|Arquivo não encontrado.").encode("utf-8"), address)
            continue
        else:
            #Pega o arquivo se ele existir
            with open(nome_arquivo, "r") as arquivo:
                conteudo = arquivo.read().encode("utf-8")

            #Calcula quantos segmentos são necessários para enviar o arquivo
            qtde_segmentos = math.ceil(len(conteudo)/TAM_CONTEUDO)
            checksum_arquivo = checksum_crc32(conteudo)
            sock.sendto(f"ACK#{qtde_segmentos}#{checksum_arquivo}|Arquivo encontrado. Iniciando transferência".encode("utf-8"), address)


        #Mensagem para fins de teste/debug
        print(f"Enviando o arquivo {nome_arquivo} para {address} em {qtde_segmentos} arquivos")

        #Se o socket levar mais que TIMEOUT_SOCKET pra responder ele vai entender que o cliente não recebeu e tentar reenviar
        sock.settimeout(TIMEOUT_SOCKET)
        #Envia cada segmento do arquivo                
        for num_segmento in range(qtde_segmentos):

            segmento = envio(address,num_segmento,conteudo)
            cache_segmentos.append(segmento)

            
           # time.sleep(0.001) #TODO: o sleep está aqui temporariamente, o pc não aguenta enviar e receber milhares de pacotes de uma vez só, mas pouco a pouco ele vai
            #TODO: ver o que é e implementar lógica de janela deslizante para controlar isso

            #Espera a resposta do cliente informando que recebeu o segmento e qual o último segmento recebeido
            try:
                confirmacao,address = sock.recvfrom(TAM_BUFFER)
                confirmacao = confirmacao.decode()
                ultimo_recebido = confirmacao.split("|")[1]
            #TODO: Implementar mais que 1 tentativa de reenvio
            #TODO: Se houverem mais que n tentativas seguidas de reenvio sem sucesso há algum problema na rede/cliente, deve-se parar o envio
            except TimeoutError:
                sock.sendto(cache_segmentos[ultimo_recebido], address)
                
    elif(mensagem_cliente.startswith("RESEND /")):
        #TODO: reenviar o segmento pedido
        num_segmento_pedido = mensagem_cliente.split("/")[1]
        print("resend")

        try:
            sock.sendto(cache_segmentos[num_segmento_pedido], address)
        except:
            sock.sendto("ERRO|segmento não encontrado".encode("utf-8"), address)

    #Envia mensagem de erro caso o comando seja inválido (diferente de GET)
    else:
        sock.sendto(("ERRO|Comando inválido").encode("utf-8"), address) 