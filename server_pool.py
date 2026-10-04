import socket
from concurrent.futures import ThreadPoolExecutor
import sys
import os

HOST = "0.0.0.0"
PORT = int(os.getenv("SERVER_PORT", "5055"))

caminho_arquivo = sys.argv[1] if len(sys.argv) > 1 else "files/arquivo_5mb.bin"

MAX_CLIENTES = int(sys.argv[2]) if len(sys.argv) > 2 else 2


def atender_cliente(conexao, endereco):
    print(f"Cliente conectado: {endereco}")

    with open(caminho_arquivo, "rb") as arquivo:
        while True:
            dados = arquivo.read(64 * 1024)

            if not dados:
                break

            conexao.sendall(dados)

    conexao.close()

    print(f"Transferência para {endereco} concluída.")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

servidor.bind((HOST, PORT))

servidor.listen()

print(
    f"Servidor com pool aguardando clientes na porta {PORT} "
    f"(máximo de {MAX_CLIENTES} simultâneos)..."
)


with ThreadPoolExecutor(max_workers=MAX_CLIENTES) as executor:

    while True:
        conexao, endereco = servidor.accept()

        executor.submit(
            atender_cliente,
            conexao,
            endereco
        )