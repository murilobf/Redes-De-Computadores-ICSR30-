"""
Requisitos do Cliente UDP:

    Inicialização: O cliente deve ser executado após o servidor estar ativo.
    FEITO Conexão: Permitir que o usuário especifique o endereço IP e a porta do servidor UDP ao qual deseja se conectar.
    Requisição:
        Enviar uma requisição ao servidor, utilizando o protocolo de aplicação definido, para solicitar um arquivo específico (Exemplo de entrada do usuário: @IP_Servidor:Porta_Servidor/nome_do_arquivo.ext).
    Simulação de Perda:
    TODO    Implementar uma opção (ex: via entrada do usuário ou configuração) que permita ao cliente descartar intencionalmente alguns segmentos recebidos do servidor. Isso é crucial para testar o mecanismo de recuperação de dados. A interface deve informar quais segmentos (ex: por número de sequência) estão sendo descartados.
    Recepção e Montagem:
    FEITO    Receber os segmentos do arquivo enviados pelo servidor.
    TODO    Armazenar e ordenar os segmentos recebidos corretamente.
    FEITO    Verificar a integridade de cada segmento (ex: usando checksum ou resumos criptográficos como o MD5 e SHA.).
    Verificação e Finalização:
    TODO    Após receber todos os segmentos esperados (ou um sinal de fim de transmissão do servidor), verificar a integridade e completude do arquivo.
    TODO    Se o arquivo estiver OK: Salvar o arquivo reconstruído localmente e informar o sucesso ao usuário. Opcionalmente, apresentar/abrir o arquivo.
    TODO    Se o arquivo estiver com erro ou incompleto:
            Identificar quais segmentos estão faltando ou corrompidos.
    TODO        Solicitar a retransmissão desses segmentos específicos ao servidor, utilizando o protocolo definido.
    TODO        Repetir o processo de recepção e verificação até que o arquivo esteja completo e correto.
    TODO        Interpretação de Erros: Interpretar e exibir mensagens de erro recebidas do servidor (ex: “Arquivo não encontrado”).


"""

import socket
import zlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

TAM_BUFFER = 4096

TIMEOUT_SOCKET = 2

#Cria o objeto de socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.settimeout(TIMEOUT_SOCKET) #Timeout do socket

def checksum_crc32(segmento):
    return zlib.crc32(segmento) & 0xffffffff

#Loop pra pegar pedir o ip mais de uma vez se precisar
while True:
    conexao = input("Insira o servidor que quer se conectar no formato IP:PORTA (Ex: 127.0.0.1:5005). ").strip()

    #Pega o IP e a porta
    try:
        udp_ip,udp_port = conexao.split(":")
        udp_port = int(udp_port)

        #Testa se a conexão existe 
        try:
            sock.sendto(b"ACK",(udp_ip,udp_port))
            data,address = sock.recvfrom(TAM_BUFFER)

            if(data.decode("utf-8").startswith("ACK")):
                break

        except TimeoutError:
            print("Tempo de resposta excedido, verifique servidor ou porta inseridos")
            continue

    except ValueError:
        print("Formato inválido, insira no formato IP:PORTA")
        continue



#Loop pra manter a conexão com o servidor

while True:

    fim_transferencia = False
    requisicao = input("Insira o nome do arquivo a ser requisito no formato GET /nome_arquivo.ext ").strip().encode("utf-8")
    sock.sendto(requisicao,(udp_ip,udp_port))
    existe_arquivo,address = sock.recvfrom(TAM_BUFFER)
    existe_arquivo = existe_arquivo.decode()

    print(existe_arquivo.split('|'))
    if(existe_arquivo.startswith("ERRO")):
        continue

    lista_segmentos = []
    qtde_segmentos_recebidos = 0

    #Loop para continuar recebendo dados até o arquivo estar completo
    while not fim_transferencia:
        data,address = sock.recvfrom(TAM_BUFFER) 
        
        data = data.decode("utf-8")

        header,conteudo = data.split('|',maxsplit=1)
        
        num_segmento, qtde_segmentos, checksum = header.split('#')
        num_segmento, qtde_segmentos, checksum = int(num_segmento), int(qtde_segmentos), int(checksum) #O cabeçalho vem em string, reconverte-os pra int

        auxChecksum = checksum_crc32(conteudo.encode("utf-8"))

        print(f"Checksum Header:{checksum}; Checksum Aqui: {auxChecksum}; Número do segmento atual: {num_segmento}")
        # print(data)

        #Se a condição abaixo for verdade, o segmento está corrompido, tem que pedir de novo
        if(checksum != auxChecksum):
            print("ERRO")
            sock.sendto(f"RESEND /{num_segmento}", (udp_ip,udp_port))
            
        else:
            qtde_segmentos_recebidos += 1

        if(qtde_segmentos_recebidos == qtde_segmentos): 
            fim_transferencia = True
            
    print("AAAAA")
    #TODO: AQUI FICARÁ A PARTE DE RECONSTRUÇÃO DO DOCUMENTO

    
