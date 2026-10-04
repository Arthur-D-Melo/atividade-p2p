from p2p_peer import receber_arquivo, enviar_arquivo


dados, tempo = receber_arquivo(
    host="localhost",
    porta=6000
)

print(f"Peer 1 recebeu o arquivo em {tempo:.4f} segundos")


enviar_arquivo(
    porta=6001,
    dados_arquivo=dados
)