"""BFS e DFS iterativas por nome ou conteúdo."""

from collections import deque
import os

from .listagem import listar_dir
from .metricas import Metricas
from .conteudo import examinar_arquivos, validar_busca


def buscar(raiz, alvo, estrategia="bfs", modo="nome"):
    """Retorne (caminhos encontrados, métricas) na primeira pasta com alvo.

    Some itens no modo nome ou bytes de texto no modo conteudo, incluindo raiz.
    Parâmetros inválidos geram ValueError antes da expansão.
    """
    if estrategia not in ("bfs", "dfs"):
        raise ValueError("Estratégia deve ser bfs ou dfs.")
    validar_busca(alvo, modo)
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
        encontrados, custo_local = examinar_arquivos(itens, termo, modo, metricas)
        custo = custo_pai + custo_local
        subpastas = []
        for item in itens:
            if item.is_dir(follow_symlinks=False):
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


def bfs(raiz, alvo, modo="nome"):
    """Busque em largura por nome ou conteúdo."""
    return buscar(raiz, alvo, "bfs", modo)


def dfs(raiz, alvo, modo="nome"):
    """Busque em profundidade por nome ou conteúdo."""
    return buscar(raiz, alvo, "dfs", modo)
