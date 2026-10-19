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
    termo = validar_busca(alvo, modo)
    return _percorrer(raiz, estrategia, termo, modo, visitas)


def _percorrer(raiz, estrategia, termo, modo, visitas):
    """Compartilhe descoberta e fronteira; termo=None é reservado ao mapeamento."""
    raiz = validar_caminho(raiz)
    fronteira = deque([(raiz, 0)])
    retirar = fronteira.popleft if estrategia == "bfs" else fronteira.pop
    visitados = {os.path.realpath(raiz)}
    mapeamento = termo is None
    descobertos = []
    metricas = Metricas()
    while fronteira:
        pasta, custo_pai = retirar()
        itens = listar_dir(pasta)
        metricas.pastas_abertas += 1
        metricas.itens_examinados += len(itens)
        if mapeamento:
            descobertos.extend(item.path for item in itens
                               if item.is_file(follow_symlinks=False))
            custo_local = len(itens)
        else:
            encontrados, custo_local = examinar_arquivos(itens, termo, modo, metricas)
        custo = custo_pai + custo_local
        if visitas is not None:
            visitas.append({"diretorio": pasta, "custo_local": custo_local, "g": custo})
        if not mapeamento and encontrados:
            metricas.arquivos_encontrados = len(encontrados)
            metricas.custo_g = custo
            return (encontrados[:1] if modo == "nome" else encontrados), metricas
        for item in (itens if estrategia == "bfs" else reversed(itens)):
            if item.is_dir(follow_symlinks=False):
                real = os.path.realpath(item.path)
                if real not in visitados:
                    visitados.add(real)
                    fronteira.append((item.path, custo))
    metricas.arquivos_encontrados = len(descobertos)
    return descobertos, metricas


def mapear(raiz, estrategia="bfs", visitas=None):
    """Etapa 1: encontre TODOS os arquivos, sem abrir conteúdos e sem alvo.

    A ordem dos resultados é a cronologia de descoberta nas expansões dos pais.
    Não há um caminho objetivo único: custo_g permanece zero. O rastro opcional
    guarda o custo do caminho de cada diretório expandido para auditoria.
    """
    if estrategia not in ("bfs", "dfs"):
        raise ValueError("Mapeamento global é permitido somente para bfs e dfs.")
    return _percorrer(raiz, estrategia, None, "nome", visitas)


def bfs(raiz, alvo, modo="nome"):
    """Busque em largura por nome ou conteúdo."""
    return buscar(raiz, alvo, "bfs", modo)


def dfs(raiz, alvo, modo="nome"):
    """Busque em profundidade por nome ou conteúdo."""
    return buscar(raiz, alvo, "dfs", modo)
