import json
import os
import socket
import time


HOST = os.getenv("SERVER_HOST", "localhost")
PORT = int(os.getenv("SERVER_PORT", "5055"))


def baixar_arquivo(host=HOST, port=PORT):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    inicio = time.perf_counter()

    cliente.connect((host, port))

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

    resultado = {
        "tempo": tempo,
        "bytes": total_recebido
    }

    arquivo_resultado = os.getenv("RESULT_FILE")

    if arquivo_resultado:
        with open(arquivo_resultado, "w") as arquivo:
            json.dump(resultado, arquivo)

    print(f"Recebidos: {total_recebido} bytes")
    print(f"Tempo: {tempo:.4f} segundos")