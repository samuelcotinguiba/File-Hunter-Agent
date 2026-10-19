"""Busca uniforme por nome ou conteúdo, com custos revelados na expansão."""

import heapq
import os

from .listagem import listar_dir
from .metricas import Metricas
from .conteudo import examinar_arquivos, validar_busca


def ucs(raiz, alvo, modo="nome"):
    """Retorne (arquivos da pasta objetivo de menor custo, métricas).

    Pastas pendentes entram com o custo do pai, um limite inferior. Expandir
    revela len(itens) ou bytes lidos; o objetivo volta ao heap com custo exato.
    Assim não é necessário listar antecipadamente nem aceitar um alvo caro
    enquanto há uma pasta pendente que pode produzir um alvo mais barato.
    """
    validar_busca(alvo, modo)
    termo = alvo.casefold()
    raiz = os.path.abspath(raiz)
    # Nó: (pasta, None) para expansão ou (pasta, correspondências) para objetivo.
    fronteira = [(0, 0, (raiz, None))]
    contador = 0
    visitados = {os.path.realpath(raiz)}
    metricas = Metricas()
    while fronteira:
        prioridade, _, (pasta, correspondencias) = heapq.heappop(fronteira)
        if correspondencias is not None:
            metricas.custo_g = prioridade
            return correspondencias, metricas
        itens = listar_dir(pasta)
        metricas.pastas_abertas += 1
        metricas.itens_examinados += len(itens)
        encontrados, custo_local = examinar_arquivos(itens, termo, modo, metricas)
        custo = prioridade + custo_local
        subpastas = []
        for item in itens:
            if item.is_dir(follow_symlinks=False):
                real = os.path.realpath(item.path)
                if real not in visitados:
                    visitados.add(real)
                    subpastas.append(item.path)
        if encontrados:
            metricas.arquivos_encontrados += len(encontrados)
            contador += 1
            heapq.heappush(fronteira, (custo, contador, (pasta, encontrados)))
        for subpasta in subpastas:
            contador += 1
            heapq.heappush(fronteira, (custo, contador, (subpasta, None)))
    return [], metricas
