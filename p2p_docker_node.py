import argparse
import json
import os
import socket
import time


CHUNK_SIZE = 64 * 1024


def criar_servidor(porta):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(("0.0.0.0", porta))
    servidor.listen(1)

    return servidor


def conectar_com_tentativas(host, porta):
    while True:
        cliente = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            cliente.connect((host, porta))
            return cliente

        except OSError:
            cliente.close()
            time.sleep(0.05)


def executar_seed(caminho_arquivo, porta):
    servidor = criar_servidor(porta)

    conexao, _ = servidor.accept()

    with open(caminho_arquivo, "rb") as arquivo:
        while True:
            dados = arquivo.read(CHUNK_SIZE)

            if not dados:
                break

            conexao.sendall(dados)

    conexao.close()
    servidor.close()


def executar_peer(
    nome,
    upstream,
    porta,
    tem_proximo,
    arquivo_resultado
):
    servidor_destino = None
    destino = None

    if tem_proximo:
        servidor_destino = criar_servidor(porta)

    origem = conectar_com_tentativas(
        upstream,
        porta
    )

    if servidor_destino is not None:
        destino, _ = servidor_destino.accept()

    inicio = time.perf_counter()

    total_recebido = 0

    while True:
        dados = origem.recv(CHUNK_SIZE)

        if not dados:
            break

        total_recebido += len(dados)

        if destino is not None:
            destino.sendall(dados)

    fim = time.perf_counter()

    origem.close()

    if destino is not None:
        destino.close()
        servidor_destino.close()

    resultado = {
        "peer": nome,
        "tempo": fim - inicio,
        "bytes": total_recebido
    }

    os.makedirs(
        os.path.dirname(arquivo_resultado),
        exist_ok=True
    )

    with open(arquivo_resultado, "w") as arquivo:
        json.dump(resultado, arquivo)


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    dest="modo",
    required=True
)


seed_parser = subparsers.add_parser("seed")

seed_parser.add_argument(
    "--file",
    required=True
)

seed_parser.add_argument(
    "--port",
    type=int,
    default=6000
)


peer_parser = subparsers.add_parser("peer")

peer_parser.add_argument(
    "--name",
    required=True
)

peer_parser.add_argument(
    "--upstream",
    required=True
)

peer_parser.add_argument(
    "--port",
    type=int,
    default=6000
)

peer_parser.add_argument(
    "--has-next",
    action="store_true"
)

peer_parser.add_argument(
    "--result",
    required=True
)


args = parser.parse_args()


if args.modo == "seed":
    executar_seed(
        args.file,
        args.port
    )

else:
    executar_peer(
        nome=args.name,
        upstream=args.upstream,
        porta=args.port,
        tem_proximo=args.has_next,
        arquivo_resultado=args.result
    )