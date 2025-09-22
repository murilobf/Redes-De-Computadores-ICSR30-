import socket
import zlib
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

TAM_BUFFER = 4096

TIMEOUT_SOCKET = 1

MAX_TENTATIVAS = 3

DESCARTAR = True

#Cria o objeto de socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.settimeout(TIMEOUT_SOCKET) #Timeout do socket

def checksum_crc32(segmento):
    return zlib.crc32(segmento) & 0xffffffff

def ordena_documento(data):
    data.sort(key=lambda segmento: int(segmento.split('#',1)[0]))
    
    return data

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

    #Mensagem informando que o arquivo existe, quantos segmentos serão enviados no total e o checksum do arquivo ao todo
    header_arquivo, conteudo_arquivo = existe_arquivo.split('|') 
    print(conteudo_arquivo)
    
    if(header_arquivo.startswith("ERRO")):
        continue
    else:
        qtde_segmentos = int(header_arquivo.split('#')[1])
        checksum_arquivo = int(header_arquivo.split('#')[2])
        print(f"Quantidade de segmentos: {qtde_segmentos}. Checksum do arquivo: {checksum_arquivo}")

    lista_segmentos = []
    qtde_segmentos_recebidos = 0
    descartado = 0

    #Loop para continuar recebendo dados até o arquivo estar completo
    while not fim_transferencia:
        recebido = False
        data,address = sock.recvfrom(TAM_BUFFER)
        
        if(data.decode().startswith("FIM")):
            fim_transferencia = True
            break
        
        #Lógica pra descartar segmentos aleatoriamente
        random_descartar = random.randint(1,100)
        if(DESCARTAR and random_descartar > 95):
            print("Descartado")
            descartado+=1
            print(descartado)
            continue

        else:
            data = data.decode("utf-8")
            #print(data)

            header,conteudo = data.split('|',maxsplit=1)
            
            num_segmento, checksum = header.split('#')
            num_segmento, checksum = int(num_segmento), int(checksum) #O cabeçalho vem em string, reconverte-os pra int

            auxChecksum = checksum_crc32(conteudo.encode("utf-8"))

            recebido = True

            #print(f"Checksum Header:{checksum}; Checksum Aqui: {auxChecksum}; Número do segmento atual: {num_segmento}")
            # print(data)

            #Se a condição abaixo for verdade, o segmento está corrompido, tem que pedir de novo
            if(checksum != auxChecksum):
                print("ERRO de checksum, pedindo segmento novamente")
                sock.sendto(f"RESEND /{num_segmento}".encode(), (udp_ip,udp_port))
                
            else:
                qtde_segmentos_recebidos += 1
                lista_segmentos.append(data)
                sock.sendto(f"ACK|{qtde_segmentos_recebidos}".encode(),(udp_ip,udp_port)) #Manda o numero do último segmento recebido para o servidor

            print(f"{qtde_segmentos_recebidos}/{qtde_segmentos}")


    print("Transnferência finalizada, montando arquivo...")
    lista_segmentos.sort(key=lambda segmento: int(segmento.split('#',1)[0]))
            
    #try:
    documento_final = ""
    num_segmento_anterior = None

    # Verifica se o documento está certo (tenta fazer isso uma quantidade máxima de vezes)
    tentativas = 0
    while tentativas < MAX_TENTATIVAS:
        documento_final = ""
        num_segmento_anterior = None

        # --- Remove duplicatas mantendo apenas o último segmento válido ---
        segmentos_unicos = {}
        for segmento in lista_segmentos:
            cabecalho, conteudo = segmento.split("|", maxsplit=1)
            num_segmento = int(cabecalho.split("#")[0])
            segmentos_unicos[num_segmento] = segmento  # sobrescreve duplicatas

        # Recria a lista ordenada sem duplicatas
        lista_segmentos = [seg for _, seg in sorted(segmentos_unicos.items())]

        # --- Identifica segmentos faltantes ---
        segmentos_recebidos = set(segmentos_unicos.keys())
        segmentos_esperados = set(range(qtde_segmentos))
        faltantes = sorted(list(segmentos_esperados - segmentos_recebidos))

        if faltantes:
            print(f"Segmentos faltantes detectados: {faltantes}")
            for num in faltantes:
                sock.sendto(f"RESEND /{num}".encode(), (udp_ip, udp_port))

            # Espera os segmentos reenviados
            try:
                while faltantes:
                    data, address = sock.recvfrom(TAM_BUFFER)
                    if data.decode().startswith("FIM"):
                        break
                    header, conteudo = data.decode("utf-8").split("|", maxsplit=1)
                    num_segmento, checksum = map(int, header.split("#"))

                    auxChecksum = checksum_crc32(conteudo.encode("utf-8"))
                    if checksum == auxChecksum:
                        lista_segmentos.append(data.decode("utf-8"))
                        if num_segmento in faltantes:
                            faltantes.remove(num_segmento)
                            sock.sendto(f"ACK|{num_segmento}".encode(), (udp_ip, udp_port))
            except socket.timeout:
                print("Timeout aguardando segmentos faltantes.")

        # --- Reconstrói o documento com os segmentos válidos ---
        lista_segmentos.sort(key=lambda segmento: int(segmento.split('#', 1)[0]))
        for segmento in lista_segmentos:
            cabecalho, conteudo = segmento.split("|", maxsplit=1)
            documento_final += conteudo

        checksum_arquivo_final = checksum_crc32(documento_final.encode())
        if checksum_arquivo_final == checksum_arquivo and len(lista_segmentos) == qtde_segmentos:
            with open(f"client/teste.txt", "w") as f:
                f.write(documento_final)
            print("Arquivo salvo com sucesso")
            break
        else:
            print("Arquivo incompleto ou corrompido, tentando novamente...")
            tentativas += 1