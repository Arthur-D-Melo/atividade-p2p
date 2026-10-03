import socket
import time

HOST = "localhost"
PORT = 5000

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

print(f"Recebidos: {total_recebido} bytes")
print(f"Tempo: {tempo:.4f} segundos")