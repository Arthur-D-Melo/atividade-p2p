from concurrent.futures import ThreadPoolExecutor
from statistics import mean

from client import baixar_arquivo

import sys

quantidade_clientes = int(sys.argv[1]) if len(sys.argv) > 1 else 4


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


print()
print(f"Tempo mínimo: {min(tempos):.4f} segundos")
print(f"Tempo médio: {mean(tempos):.4f} segundos")
print(f"Tempo máximo: {max(tempos):.4f} segundos")