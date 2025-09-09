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
    TODO    O arquivo a ser transmitido deve ser relativamente grande (ex: > 1 MB) para justificar a segmentação.
    TODO    Segmentação: Dividir o arquivo em múltiplos segmentos/pedaços para envio em datagramas UDP.
    TODO    Cabeçalho Customizado: Cada segmento enviado deve conter informações de controle definidas pelo seu protocolo (ver “Considerações de Protocolo” abaixo).
    TODO    Retransmissão: Implementar lógica para reenviar segmentos específicos caso o cliente solicite (devido a perdas ou erros).


"""

import socket
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

BUFFER_SIZE = 1024

# Cria o objeto de tipo socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT)) #O servidor fica ouvindo nessa porta

#Envia a mensagem no formato (mensagem (IP, PORT))só pra ter como base
#sock.sendto(b"hello world", (UDP_IP, UDP_PORT))

#Loop pra simular a conexão
while True:

    data,address = sock.recvfrom(BUFFER_SIZE) #Espera um novo cliente

    mensagem_cliente = data.decode("raw-unicode-escape") #Decodifica

    if(mensagem_cliente.startswith("GET")):
        _,nome_arquivo = mensagem_cliente.split(maxsplit=1) #O maxsplit é mais pra garantir que não haja espaços em branco

        #Pega o arquivo se ele existir
        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, "r") as arquivo:
                resposta = arquivo.read()

        else:
            resposta = "ERRO: Arquivo não encontrado."

    else:
        resposta = "ERRO: Comando inválido"

    #Retorna a resposta (seja o arquivo ou os erros)
    sock.sendto(resposta.encode(), address)

