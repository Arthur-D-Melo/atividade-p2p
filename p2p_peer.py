import socket
import time

CHUNK_SIZE = 64 * 1024


def receber_arquivo(host, porta):
    inicio = time.perf_counter()

    while True:
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((host, porta))
            break
        except ConnectionRefusedError:
            time.sleep(0.05)

    dados_recebidos = bytearray()

    while True:
        dados = cliente.recv(CHUNK_SIZE)

        if not dados:
            break

        dados_recebidos.extend(dados)

    cliente.close()

    fim = time.perf_counter()

    tempo = fim - inicio

    return bytes(dados_recebidos), tempo


def enviar_arquivo(porta, dados_arquivo):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(("0.0.0.0", porta))

    servidor.listen(1)

    print(f"Aguardando outro peer na porta {porta}...")

    conexao, endereco = servidor.accept()

    print(f"Peer conectado: {endereco}")

    conexao.sendall(dados_arquivo)

    conexao.close()
    servidor.close()

    print("Arquivo enviado para o próximo peer.")