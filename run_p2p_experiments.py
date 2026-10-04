import csv
import time

from p2p_benchmark import executar_benchmark_p2p


ARQUIVOS = {
    5: "files/arquivo_5mb.bin",
    50: "files/arquivo_50mb.bin",
    500: "files/arquivo_500mb.bin"
}

QUANTIDADES_PEERS = [1, 2, 4, 8]

ARQUIVO_RESULTADOS = "results/resultados_p2p.csv"


with open(
    ARQUIVO_RESULTADOS,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "arquitetura",
        "tamanho_mb",
        "clientes",
        "minimo",
        "medio",
        "maximo"
    ])

    for tamanho_mb, caminho in ARQUIVOS.items():

        for quantidade in QUANTIDADES_PEERS:

            print()
            print(
                f"Testando P2P | "
                f"{tamanho_mb} MB | "
                f"{quantidade} peers"
            )

            resultado = executar_benchmark_p2p(
                caminho,
                quantidade
            )

            writer.writerow([
                "p2p",
                tamanho_mb,
                quantidade,
                resultado["minimo"],
                resultado["medio"],
                resultado["maximo"]
            ])

            csvfile.flush()

            print(
                f"Resultado: "
                f"min={resultado['minimo']:.4f}s | "
                f"média={resultado['medio']:.4f}s | "
                f"max={resultado['maximo']:.4f}s"
            )

            time.sleep(0.2)


print()
print("Experimentos P2P concluídos.")
print(f"Resultados salvos em: {ARQUIVO_RESULTADOS}")