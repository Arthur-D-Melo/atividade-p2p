import csv
import json
import shutil
import subprocess
import time

from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent

IMAGE = "atividade-p2p-benchmark"
NETWORK = "atividade-p2p-network"

PORTA_SERVIDOR = 5055
PORTA_P2P = 6000

ARQUIVOS = {
    5: "arquivo_5mb.bin",
    50: "arquivo_50mb.bin",
    500: "arquivo_500mb.bin"
}

QUANTIDADES = [1, 2, 4, 8]

ARQUITETURAS = {
    "sequencial": "server.py",
    "threads": "server_threads.py",
    "pool": "server_pool.py"
}

PASTA_RESULTADOS = ROOT / "results" / "docker"

CSV_FINAL = (
    ROOT
    / "results"
    / "resultados_docker.csv"
)


def criar_arquivos_teste():
    tamanhos = {
        "arquivo_5mb.bin": 5 * 1024 * 1024,
        "arquivo_50mb.bin": 50 * 1024 * 1024,
        "arquivo_500mb.bin": 500 * 1024 * 1024
    }

    pasta = ROOT / "files"

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    for nome, tamanho in tamanhos.items():
        caminho = pasta / nome

        if not caminho.exists():
            print(f"Criando {nome}...")

            with open(caminho, "wb") as arquivo:
                arquivo.truncate(tamanho)


def executar(comando):
    subprocess.run(
        comando,
        check=True,
        cwd=ROOT
    )


def remover_container(nome):
    subprocess.run(
        [
            "docker",
            "rm",
            "-f",
            nome
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def preparar_docker():
    print("Construindo imagem Docker...")

    executar([
        "docker",
        "build",
        "-t",
        IMAGE,
        "."
    ])

    subprocess.run(
        [
            "docker",
            "network",
            "rm",
            NETWORK
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    executar([
        "docker",
        "network",
        "create",
        NETWORK
    ])


def criar_pasta_cenario(nome):
    pasta = PASTA_RESULTADOS / nome

    if pasta.exists():
        shutil.rmtree(pasta)

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    return pasta


def esperar_processo(processo, nome):
    try:
        codigo = processo.wait(
            timeout=300
        )

    except subprocess.TimeoutExpired:
        processo.kill()

        raise RuntimeError(
            f"Timeout no container {nome}"
        )

    if codigo != 0:
        erro = processo.stderr.read()

        raise RuntimeError(
            f"Erro no container {nome}:\n{erro}"
        )


def experimento_cliente_servidor(
    arquitetura,
    script_servidor,
    tamanho_mb,
    arquivo,
    quantidade
):
    nome_cenario = (
        f"{arquitetura}_"
        f"{tamanho_mb}mb_"
        f"{quantidade}"
    )

    pasta = criar_pasta_cenario(
        nome_cenario
    )

    remover_container(
        "bench-server"
    )

    for numero in range(
        1,
        quantidade + 1
    ):
        remover_container(
            f"bench-client-{numero}"
        )

    volume_files = (
        f"{ROOT / 'files'}:/app/files:ro"
    )

    comando_servidor = [
        "docker",
        "run",
        "--rm",
        "--name",
        "bench-server",
        "--network",
        NETWORK,
        "-e",
        f"SERVER_PORT={PORTA_SERVIDOR}",
        "-v",
        volume_files,
        IMAGE,
        "python",
        script_servidor,
        f"files/{arquivo}"
    ]

    if arquitetura == "pool":
        comando_servidor.append("2")

    servidor = subprocess.Popen(
        comando_servidor,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(1)

    if servidor.poll() is not None:
        erro = servidor.stderr.read()

        raise RuntimeError(
            f"Erro ao iniciar {script_servidor}:\n{erro}"
        )

    clientes = []

    volume_resultados = (
        f"{pasta}:/results"
    )

    for numero in range(
        1,
        quantidade + 1
    ):
        comando_cliente = [
            "docker",
            "run",
            "--rm",
            "--name",
            f"bench-client-{numero}",
            "--network",
            NETWORK,
            "-e",
            "SERVER_HOST=bench-server",
            "-e",
            f"SERVER_PORT={PORTA_SERVIDOR}",
            "-e",
            (
                "RESULT_FILE="
                f"/results/client_{numero}.json"
            ),
            "-v",
            volume_resultados,
            IMAGE,
            "python",
            "client.py"
        ]

        processo = subprocess.Popen(
            comando_cliente,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        clientes.append(
            (
                numero,
                processo
            )
        )

    for numero, processo in clientes:
        esperar_processo(
            processo,
            f"cliente {numero}"
        )

    remover_container(
        "bench-server"
    )

    try:
        servidor.wait(
            timeout=5
        )

    except subprocess.TimeoutExpired:
        servidor.kill()

    tempos = []

    for numero in range(
        1,
        quantidade + 1
    ):
        caminho = (
            pasta
            / f"client_{numero}.json"
        )

        with open(caminho) as arquivo_json:
            resultado = json.load(
                arquivo_json
            )

        tempos.append(
            resultado["tempo"]
        )

    return {
        "minimo": min(tempos),
        "medio": mean(tempos),
        "maximo": max(tempos)
    }


def experimento_p2p(
    tamanho_mb,
    arquivo,
    quantidade
):
    nome_cenario = (
        f"p2p_"
        f"{tamanho_mb}mb_"
        f"{quantidade}"
    )

    pasta = criar_pasta_cenario(
        nome_cenario
    )

    remover_container(
        "p2p-seed"
    )

    for numero in range(
        1,
        quantidade + 1
    ):
        remover_container(
            f"p2p-peer-{numero}"
        )

    volume_resultados = (
        f"{pasta}:/results"
    )

    peers = []

    for numero in range(
        quantidade,
        0,
        -1
    ):
        if numero == 1:
            upstream = "p2p-seed"

        else:
            upstream = (
                f"p2p-peer-{numero - 1}"
            )

        comando = [
            "docker",
            "run",
            "--rm",
            "--name",
            f"p2p-peer-{numero}",
            "--network",
            NETWORK,
            "-v",
            volume_resultados,
            IMAGE,
            "python",
            "p2p_docker_node.py",
            "peer",
            "--name",
            f"peer{numero}",
            "--upstream",
            upstream,
            "--port",
            str(PORTA_P2P),
            "--result",
            (
                f"/results/"
                f"peer_{numero}.json"
            )
        ]

        if numero < quantidade:
            comando.append(
                "--has-next"
            )

        processo = subprocess.Popen(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        peers.append(
            (
                numero,
                processo
            )
        )

        time.sleep(0.05)

    volume_files = (
        f"{ROOT / 'files'}:/app/files:ro"
    )

    comando_seed = [
        "docker",
        "run",
        "--rm",
        "--name",
        "p2p-seed",
        "--network",
        NETWORK,
        "-v",
        volume_files,
        IMAGE,
        "python",
        "p2p_docker_node.py",
        "seed",
        "--file",
        f"files/{arquivo}",
        "--port",
        str(PORTA_P2P)
    ]

    seed = subprocess.Popen(
        comando_seed,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    for numero, processo in peers:
        esperar_processo(
            processo,
            f"peer {numero}"
        )

    esperar_processo(
        seed,
        "seed"
    )

    tempos = []

    for numero in range(
        1,
        quantidade + 1
    ):
        caminho = (
            pasta
            / f"peer_{numero}.json"
        )

        with open(caminho) as arquivo_json:
            resultado = json.load(
                arquivo_json
            )

        tempos.append(
            resultado["tempo"]
        )

    return {
        "minimo": min(tempos),
        "medio": mean(tempos),
        "maximo": max(tempos)
    }


def main():
    criar_arquivos_teste()

    PASTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    preparar_docker()

    with open(
        CSV_FINAL,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(
            csvfile
        )

        writer.writerow([
            "arquitetura",
            "tamanho_mb",
            "clientes",
            "minimo",
            "medio",
            "maximo"
        ])

        for arquitetura, script in (
            ARQUITETURAS.items()
        ):
            for tamanho_mb, arquivo in (
                ARQUIVOS.items()
            ):
                for quantidade in QUANTIDADES:

                    print(
                        f"\n{arquitetura} | "
                        f"{tamanho_mb} MB | "
                        f"{quantidade} clientes"
                    )

                    resultado = (
                        experimento_cliente_servidor(
                            arquitetura,
                            script,
                            tamanho_mb,
                            arquivo,
                            quantidade
                        )
                    )

                    writer.writerow([
                        arquitetura,
                        tamanho_mb,
                        quantidade,
                        resultado["minimo"],
                        resultado["medio"],
                        resultado["maximo"]
                    ])

                    csvfile.flush()

                    print(
                        f"min={resultado['minimo']:.4f}s | "
                        f"média={resultado['medio']:.4f}s | "
                        f"max={resultado['maximo']:.4f}s"
                    )

        for tamanho_mb, arquivo in (
            ARQUIVOS.items()
        ):
            for quantidade in QUANTIDADES:

                print(
                    f"\nP2P | "
                    f"{tamanho_mb} MB | "
                    f"{quantidade} peers"
                )

                resultado = experimento_p2p(
                    tamanho_mb,
                    arquivo,
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
                    f"min={resultado['minimo']:.4f}s | "
                    f"média={resultado['medio']:.4f}s | "
                    f"max={resultado['maximo']:.4f}s"
                )

    subprocess.run(
        [
            "docker",
            "network",
            "rm",
            NETWORK
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print()
    print("Todos os experimentos terminaram.")
    print(
        f"Resultados: {CSV_FINAL}"
    )


if __name__ == "__main__":
    main()