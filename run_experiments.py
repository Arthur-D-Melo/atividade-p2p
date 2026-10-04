import csv
import subprocess
import sys
import time

from benchmark import executar_benchmark


ARQUIVOS = {
    5: "files/arquivo_5mb.bin",
    50: "files/arquivo_50mb.bin",
    500: "files/arquivo_500mb.bin"
}

QUANTIDADES_CLIENTES = [1, 2, 4, 8]

ARQUITETURAS = [
    ("sequencial", "server.py"),
    ("threads", "server_threads.py"),
    ("pool", "server_pool.py")
]

ARQUIVO_RESULTADOS = "results/resultados_cliente_servidor.csv"


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

    for arquitetura, script_servidor in ARQUITETURAS:

        for tamanho_mb, caminho_arquivo in ARQUIVOS.items():

            for quantidade_clientes in QUANTIDADES_CLIENTES:

                print()
                print(
                    f"Testando {arquitetura} | "
                    f"{tamanho_mb} MB | "
                    f"{quantidade_clientes} clientes"
                )

                comando = [
                    sys.executable,
                    script_servidor,
                    caminho_arquivo
                ]

                if arquitetura == "pool":
                    comando.append("2")

                servidor = subprocess.Popen(
                    comando,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True
                )

                time.sleep(0.5)

                if servidor.poll() is not None:
                    erro = servidor.stderr.read()
                    raise RuntimeError(
                        f"Erro ao iniciar {script_servidor}:\n{erro}"
                    )

                try:
                    resultado = executar_benchmark(
                        quantidade_clientes
                    )

                    writer.writerow([
                        arquitetura,
                        tamanho_mb,
                        quantidade_clientes,
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

                finally:
                    servidor.terminate()

                    try:
                        servidor.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        servidor.kill()

                    time.sleep(0.2)


print()
print("Experimentos concluídos.")
print(f"Resultados salvos em: {ARQUIVO_RESULTADOS}")