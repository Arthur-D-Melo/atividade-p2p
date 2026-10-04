import threading
from statistics import mean

from p2p_peer import receber_arquivo, enviar_arquivo


CAMINHO_ARQUIVO = "files/arquivo_5mb.bin"
PORTA_INICIAL = 6000
QUANTIDADE_PEERS = 4


resultados = []


def executar_seed():
    with open(CAMINHO_ARQUIVO, "rb") as arquivo:
        dados = arquivo.read()

    enviar_arquivo(
        porta=PORTA_INICIAL,
        dados_arquivo=dados
    )


def executar_peer(numero):
    porta_origem = PORTA_INICIAL + numero - 1

    dados, tempo = receber_arquivo(
        host="localhost",
        porta=porta_origem
    )

    resultados.append(
        (numero, tempo, len(dados))
    )

    if numero < QUANTIDADE_PEERS:
        porta_destino = PORTA_INICIAL + numero

        enviar_arquivo(
            porta=porta_destino,
            dados_arquivo=dados
        )


thread_seed = threading.Thread(
    target=executar_seed
)

thread_seed.start()


threads_peers = []

for numero in range(1, QUANTIDADE_PEERS + 1):
    thread = threading.Thread(
        target=executar_peer,
        args=(numero,)
    )

    thread.start()

    threads_peers.append(thread)


for thread in threads_peers:
    thread.join()


thread_seed.join()


resultados.sort()

tempos = []


for numero, tempo, total_recebido in resultados:
    tempos.append(tempo)

    print(
        f"Peer {numero}: "
        f"{total_recebido} bytes em {tempo:.4f} segundos"
    )


print()
print(f"Tempo mínimo: {min(tempos):.4f} segundos")
print(f"Tempo médio: {mean(tempos):.4f} segundos")
print(f"Tempo máximo: {max(tempos):.4f} segundos")