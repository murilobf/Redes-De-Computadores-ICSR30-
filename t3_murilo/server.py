import socket
import threading
import os

TAM_BUFFER = 4096
PORTA = 5006

def processar_cliente(conexao, endereco):
    with clientes_lock:
        clientes_conectados.append(conexao)

    try:
        dado = conexao.recv(TAM_BUFFER)
        
        if not dado:
            print(f"Cliente {endereco} desconectado. Eliminando thread.")

        dado = dado.decode()

        primeira_linha = dado.split('\n')[0]
        print(primeira_linha)
        requisicao = primeira_linha.split(' ')[0]
        caminho_arquivo = primeira_linha.split(' ')[1]
        caminho_arquivo = caminho_arquivo.split('/')[1]
        if(caminho_arquivo == ''):
                    caminho_arquivo = 'imagens.html'

        if(caminho_arquivo.endswith('.html')):
            tipo_conteudo = 'text/html'
        elif(caminho_arquivo.endswith('.jpeg') or caminho_arquivo.endswith('.jpg')):
            tipo_conteudo = 'image/jpeg'
        elif(caminho_arquivo.endswith('.png')):
            tipo_conteudo = 'image/png'

        try:
            if requisicao.startswith("GET"): #Dá pra pegar a primeira linha da requisição http
                print(f"Cliente: {endereco} solicitando: {caminho_arquivo}")

                if not os.path.exists(caminho_arquivo):
                    corpo = (
                        f"<html>"
                        f"<head><title>404 Not Found</title></head>"
                        f"<body><h1>404 Não encontrado</h1><p>O arquivo '{caminho_arquivo}' nao foi encontrado.</p></body>"
                        f"</html>"
                    ).encode()

                    header = (
                        "HTTP/1.1 404 Not Found\r\n"
                        "Content-Type: text/html\r\n"
                        f"Content-Length {len(corpo)}\r\n"
                        "\r\n"
                    ).encode()

                    resposta = header+corpo
                    conexao.sendall(resposta)
                    conexao.close()

                else:
                    with open(caminho_arquivo, 'rb') as arquivo:
                        conteudo = arquivo.read()

                        tam_arquivo = (len(conteudo))

                        header = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: {tipo_conteudo}\r\n"
                        f"Content-Length: {tam_arquivo}\r\n"
                        f"Connection: keep-alive\r\n"
                        f"\r\n"
                        ).encode()
                        conexao.sendall(header)

                        
                        arquivo.seek(0)
                        while True:
                            bloco = arquivo.read(TAM_BUFFER)
                            if not bloco:
                                break
                            conexao.sendall(bloco)
                    conexao.close()


            else:
                corpo_erro = (
                    f"<html>"
                    f"<head><title>400 Bad Request</title></head>"
                    f"<body><h1>400 Bad Request</h1><p>Comando inválido.</p></body>"
                    f"</html>"
                ).encode()

                header_erro = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(corpo_erro)}\r\n"
                    "\r\n"
                ).encode()

                conexao.sendall(header_erro + corpo_erro)


        except Exception as e:
            print(e)
            corpo_erro = (
                f"<html>"
                f"<head><title>400 Bad Request</title></head>"
                f"<body><h1>400 Bad Request</h1><p>Comando inválido.</p></body>"
                f"</html>"
            ).encode()

            header_erro = (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(corpo_erro)}\r\n"
                "\r\n"
            ).encode()

            conexao.sendall(header_erro + corpo_erro)

            
    finally:
        with clientes_lock:
            if(conexao in clientes_conectados):
                clientes_conectados.remove(conexao)
                conexao.close()

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("127.0.0.1", PORTA))
servidor.listen(5)

clientes_conectados = []
clientes_lock = threading.Lock()

print(f"SERVIDOR INICIALIZADO no IP: http://127.0.0.1:{PORTA}/.")

while True:
    conexao, endereco = servidor.accept()

    print(f"Criando thread para cliente {endereco}")
    thread_cliente = threading.Thread(target=processar_cliente, args=(conexao,endereco))
    thread_cliente.start()