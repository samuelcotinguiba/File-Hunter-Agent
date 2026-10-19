"""BFS e DFS iterativas por nome, com descoberta na expansão do pai."""

from collections import deque
import os

from .listagem import listar_dir
from .metricas import Metricas


def buscar(raiz, alvo, estrategia="bfs"):
    """Retorne (caminhos encontrados, métricas) na primeira pasta com alvo.

    O custo soma os tamanhos das listagens do caminho, incluindo a raiz.
    Não lê conteúdos. Um alvo vazio ou estratégia desconhecida gera ValueError.
    """
    if estrategia not in ("bfs", "dfs"):
        raise ValueError("Estratégia deve ser bfs ou dfs.")
    if not alvo:
        raise ValueError("O alvo não pode ser vazio.")
    termo = alvo.casefold()
    fronteira = deque([(os.path.abspath(raiz), 0)])
    visitados = {os.path.realpath(raiz)}
    metricas = Metricas()
    while fronteira:
        pasta, custo_pai = (fronteira.popleft() if estrategia == "bfs"
                            else fronteira.pop())
        itens = listar_dir(pasta)
        metricas.pastas_abertas += 1
        metricas.itens_examinados += len(itens)
        custo = custo_pai + len(itens)
        encontrados = []
        subpastas = []
        for item in itens:
            if item.is_file(follow_symlinks=False):
                if termo in item.name.casefold():
                    encontrados.append(item.path)
            elif item.is_dir(follow_symlinks=False):
                real = os.path.realpath(item.path)
                if real not in visitados:
                    visitados.add(real)
                    subpastas.append((item.path, custo))
        if encontrados:
            metricas.arquivos_encontrados = len(encontrados)
            metricas.custo_g = custo
            return encontrados, metricas
        fronteira.extend(subpastas if estrategia == "bfs" else reversed(subpastas))
    return [], metricas


def bfs(raiz, alvo):
    """Busque por nome em largura."""
    return buscar(raiz, alvo, "bfs")


def dfs(raiz, alvo):
    """Busque por nome em profundidade."""
    return buscar(raiz, alvo, "dfs")
