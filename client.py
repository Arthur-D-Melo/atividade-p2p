import socket
import time

HOST = "localhost"
PORT = 5055


def baixar_arquivo():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    inicio = time.perf_counter()

    cliente.connect((HOST, PORT))

    total_recebido = 0

    while True:
        dados = cliente.recv(64 * 1024)

        if not dados:
            break

        total_recebido += len(dados)

    fim = time.perf_counter()

    cliente.close()

    tempo = fim - inicio

    return tempo, total_recebido


if __name__ == "__main__":
    tempo, total_recebido = baixar_arquivo()

    print(f"Recebidos: {total_recebido} bytes")
    print(f"Tempo: {tempo:.4f} segundos")