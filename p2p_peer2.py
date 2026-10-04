from p2p_peer import receber_arquivo


dados, tempo = receber_arquivo(
    host="localhost",
    porta=6001
)

print(f"Peer 2 recebeu o arquivo em {tempo:.4f} segundos")
print(f"Total recebido: {len(dados)} bytes")