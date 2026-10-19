"""BFS e DFS iterativas por nome ou conteúdo."""

from collections import deque
import os

from .listagem import listar_dir, validar_caminho
from .metricas import Metricas
from .conteudo import examinar_arquivos, validar_busca


def buscar(raiz, alvo, estrategia="bfs", modo="nome", visitas=None):
    """Retorne (caminhos encontrados, métricas) na pasta objetivo.

    Some itens no modo nome ou bytes de texto no modo conteudo, incluindo raiz.
    Nome seleciona o primeiro arquivo; conteúdo mantém os correspondentes da pasta.
    visitas, se fornecida, recebe a cronologia de diretórios e seus custos.
    Parâmetros inválidos geram ValueError antes da expansão.
    """
    if estrategia not in ("bfs", "dfs"):
        raise ValueError("Estratégia deve ser bfs ou dfs.")
    validar_busca(alvo, modo)
    termo = alvo.casefold()
    raiz = validar_caminho(raiz)
    fronteira = deque([(raiz, 0)])
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
        if visitas is not None:
            visitas.append({"diretorio": pasta, "custo_local": custo_local, "g": custo})
        if encontrados:
            metricas.arquivos_encontrados = len(encontrados)
            metricas.custo_g = custo
            return (encontrados[:1] if modo == "nome" else encontrados), metricas
        subpastas = []
        for item in itens:
            if item.is_dir(follow_symlinks=False):
                real = os.path.realpath(item.path)
                if real not in visitados:
                    visitados.add(real)
                    subpastas.append((item.path, custo))
        fronteira.extend(subpastas if estrategia == "bfs" else reversed(subpastas))
    return [], metricas


def mapear(raiz, estrategia="bfs", visitas=None):
    """Etapa 1: encontre TODOS os arquivos, sem abrir conteúdos e sem alvo.

    A ordem dos resultados é a cronologia de descoberta nas expansões dos pais.
    Não há um caminho objetivo único: custo_g permanece zero. O rastro opcional
    guarda o custo do caminho de cada diretório expandido para auditoria.
    """
    if estrategia not in ("bfs", "dfs"):
        raise ValueError("Mapeamento global é permitido somente para bfs e dfs.")
    raiz = validar_caminho(raiz)
    fronteira = deque([(raiz, 0)])
    visitados = {os.path.realpath(raiz)}
    encontrados = []
    metricas = Metricas()
    while fronteira:
        pasta, custo_pai = (fronteira.popleft() if estrategia == "bfs" else fronteira.pop())
        itens = listar_dir(pasta)
        metricas.pastas_abertas += 1
        metricas.itens_examinados += len(itens)
        custo = custo_pai + len(itens)
        if visitas is not None:
            visitas.append({"diretorio": pasta, "custo_local": len(itens), "g": custo})
        subpastas = []
        for item in itens:
            if item.is_file(follow_symlinks=False):
                encontrados.append(item.path)
                metricas.arquivos_encontrados += 1
            elif item.is_dir(follow_symlinks=False):
                real = os.path.realpath(item.path)
                if real not in visitados:
                    visitados.add(real)
                    subpastas.append((item.path, custo))
        fronteira.extend(subpastas if estrategia == "bfs" else reversed(subpastas))
    return encontrados, metricas


def bfs(raiz, alvo, modo="nome"):
    """Busque em largura por nome ou conteúdo."""
    return buscar(raiz, alvo, "bfs", modo)


def dfs(raiz, alvo, modo="nome"):
    """Busque em profundidade por nome ou conteúdo."""
    return buscar(raiz, alvo, "dfs", modo)
