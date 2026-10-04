# Atividade U2 - Sistemas Distribuídos

Projeto desenvolvido para comparar o desempenho de diferentes formas de transferência de arquivos.

Foram implementadas quatro abordagens:

- servidor sequencial, atendendo um cliente por vez;
- servidor com uma thread para cada cliente;
- servidor com pool limitado a 2 clientes simultâneos;
- transferência P2P simplificada.

Os testes foram realizados com arquivos de 5 MB, 50 MB e 500 MB, utilizando 1, 2, 4 e 8 clientes ou peers.

Para simular nós separados, os testes finais foram executados com containers Docker conectados pela mesma rede Docker.

## Arquivos principais

- `server.py`: servidor sequencial
- `server_threads.py`: servidor com uma thread por cliente
- `server_pool.py`: servidor com limite de clientes simultâneos
- `client.py`: cliente usado nas transferências
- `p2p_docker_node.py`: implementação usada nos testes P2P com Docker
- `run_docker_benchmarks.py`: executa os experimentos finais
- `results/`: resultados dos experimentos
- `relatorio/`: relatório final da atividade

## Executando os experimentos

É necessário ter Python e Docker instalados.

Com o Docker em execução, rode:

```bash
python run_docker_benchmarks.py
```

Os arquivos de 5 MB, 50 MB e 500 MB são criados automaticamente caso ainda não existam.

Os resultados dos testes são salvos na pasta `results/`.

O relatório final da atividade pode ser encontrado na pasta `relatorio/`.