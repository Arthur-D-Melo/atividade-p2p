from p2p_peer import enviar_arquivo


caminho_arquivo = "files/arquivo_5mb.bin"


with open(caminho_arquivo, "rb") as arquivo:
    dados_arquivo = arquivo.read()


print("Seed iniciado.")

enviar_arquivo(
    porta=6000,
    dados_arquivo=dados_arquivo
)