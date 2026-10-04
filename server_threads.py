import socket
import threading
import sys

HOST = "0.0.0.0"
PORT = 5000

caminho_arquivo = sys.argv[1] if len(sys.argv) > 1 else "files/arquivo_5mb.bin"


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

servidor.bind((HOST, PORT))

servidor.listen()

print(f"Servidor com threads aguardando clientes na porta {PORT}...")


while True:
    conexao, endereco = servidor.accept()

    thread = threading.Thread(
        target=atender_cliente,
        args=(conexao, endereco)
    )

    thread.start()