import sys

from concurrent.futures import ThreadPoolExecutor
from statistics import mean

from client import baixar_arquivo


def executar_benchmark(quantidade_clientes):

    with ThreadPoolExecutor(max_workers=quantidade_clientes) as executor:
        resultados = list(
            executor.map(
                lambda _: baixar_arquivo(),
                range(quantidade_clientes)
            )
        )

    tempos = []

    for indice, resultado in enumerate(resultados, start=1):
        tempo, total_recebido = resultado

        tempos.append(tempo)

        print(
            f"Cliente {indice}: "
            f"{total_recebido} bytes em {tempo:.4f} segundos"
        )

    return {
        "minimo": min(tempos),
        "medio": mean(tempos),
        "maximo": max(tempos)
    }


if __name__ == "__main__":

    quantidade_clientes = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    resultado = executar_benchmark(quantidade_clientes)

    print()
    print(f"Tempo mínimo: {resultado['minimo']:.4f} segundos")
    print(f"Tempo médio: {resultado['medio']:.4f} segundos")
    print(f"Tempo máximo: {resultado['maximo']:.4f} segundos")