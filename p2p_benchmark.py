import sys
import threading

from statistics import mean
from p2p_peer import enviar_arquivo, receber_e_repassar


PORTA_INICIAL = 6000


def executar_benchmark_p2p(caminho_arquivo, quantidade_peers):
    resultados = []
    lock = threading.Lock()

    def executar_seed():
        enviar_arquivo(
            porta=PORTA_INICIAL,
            caminho_arquivo=caminho_arquivo
        )

    def executar_peer(numero):
        porta_origem = PORTA_INICIAL + numero - 1

        if numero < quantidade_peers:
            porta_destino = PORTA_INICIAL + numero
        else:
            porta_destino = None

        total, tempo = receber_e_repassar(
            host="localhost",
            porta_origem=porta_origem,
            porta_destino=porta_destino
        )

        with lock:
            resultados.append(
                (numero, tempo, total)
            )

    thread_seed = threading.Thread(
        target=executar_seed
    )

    thread_seed.start()

    threads = []

    for numero in range(1, quantidade_peers + 1):
        thread = threading.Thread(
            target=executar_peer,
            args=(numero,)
        )

        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    thread_seed.join()

    resultados.sort()

    tempos = []

    for numero, tempo, total in resultados:
        tempos.append(tempo)

        print(
            f"Peer {numero}: "
            f"{total} bytes em {tempo:.4f} segundos"
        )

    return {
        "minimo": min(tempos),
        "medio": mean(tempos),
        "maximo": max(tempos)
    }


if __name__ == "__main__":
    caminho = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "files/arquivo_5mb.bin"
    )

    quantidade = (
        int(sys.argv[2])
        if len(sys.argv) > 2
        else 4
    )

    resultado = executar_benchmark_p2p(
        caminho,
        quantidade
    )

    print()
    print(f"Tempo mínimo: {resultado['minimo']:.4f} segundos")
    print(f"Tempo médio: {resultado['medio']:.4f} segundos")
    print(f"Tempo máximo: {resultado['maximo']:.4f} segundos")