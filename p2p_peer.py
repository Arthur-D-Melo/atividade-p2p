import socket
import time

CHUNK_SIZE = 64 * 1024


def conectar_com_tentativas(host, porta):
    while True:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            cliente.connect((host, porta))
            return cliente
        except ConnectionRefusedError:
            cliente.close()
            time.sleep(0.05)


def enviar_arquivo(porta, caminho_arquivo):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(("0.0.0.0", porta))
    servidor.listen(1)

    conexao, endereco = servidor.accept()

    with open(caminho_arquivo, "rb") as arquivo:
        while True:
            dados = arquivo.read(CHUNK_SIZE)

            if not dados:
                break

            conexao.sendall(dados)

    conexao.close()
    servidor.close()


def receber_e_repassar(host, porta_origem, porta_destino=None):
    inicio = time.perf_counter()

    origem = conectar_com_tentativas(
        host,
        porta_origem
    )

    destino = None
    servidor_destino = None

    if porta_destino is not None:
        servidor_destino = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        servidor_destino.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        servidor_destino.bind(
            ("0.0.0.0", porta_destino)
        )

        servidor_destino.listen(1)

        destino, _ = servidor_destino.accept()

    total_recebido = 0

    while True:
        dados = origem.recv(CHUNK_SIZE)

        if not dados:
            break

        total_recebido += len(dados)

        if destino is not None:
            destino.sendall(dados)

    origem.close()

    if destino is not None:
        destino.close()
        servidor_destino.close()

    fim = time.perf_counter()

    return total_recebido, fim - inicio