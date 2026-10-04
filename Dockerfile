FROM python:3.12-slim

WORKDIR /app

COPY client.py .
COPY server.py .
COPY server_threads.py .
COPY server_pool.py .
COPY p2p_docker_node.py .

CMD ["python", "--version"]