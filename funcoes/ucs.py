"""Busca uniforme por nome ou conteúdo, com custos revelados na expansão."""

import heapq
import os

from .listagem import listar_dir, validar_caminho
from .metricas import Metricas
from .conteudo import examinar_arquivos, validar_busca


def ucs(raiz, alvo, modo="nome", visitas=None):
    """Retorne (arquivos da pasta objetivo de menor custo, métricas).

    Pastas pendentes entram com o custo do pai, um limite inferior. Expandir
    revela len(itens) ou bytes lidos; o objetivo volta ao heap com custo exato.
    Assim não é necessário listar antecipadamente nem aceitar um alvo caro
    enquanto há uma pasta pendente que pode produzir um alvo mais barato.
    """
    return _buscar_prioridade(raiz, alvo, modo, visitas=visitas)


def _buscar_prioridade(raiz, alvo, modo, estimar=None, visitas=None):
    """Motor de heap: UCS sem estimativa, A* com estimativa para pastas pendentes.

    Guarde g no nó, separado da prioridade f. Objetivos já confirmados têm h=0.
    O custo local só é conhecido na expansão, mantendo a avaliação adiada de UCS.
    """
    validar_busca(alvo, modo)
    termo = alvo.casefold()
    raiz = validar_caminho(raiz)
    # Nó: (pasta, correspondências ou None, g exato ou custo do pai).
    prioridade_raiz = estimar(raiz) if estimar else 0
    fronteira = [(prioridade_raiz, 0, (raiz, None, 0))]
    contador = 0
    visitados = {os.path.realpath(raiz)}
    metricas = Metricas()
    while fronteira:
        _, _, (pasta, correspondencias, g) = heapq.heappop(fronteira)
        if correspondencias is not None:
            metricas.custo_g = g
            return (correspondencias[:1] if modo == "nome" else correspondencias), metricas
        itens = listar_dir(pasta)
        metricas.pastas_abertas += 1
        metricas.itens_examinados += len(itens)
        encontrados, custo_local = examinar_arquivos(itens, termo, modo, metricas)
        custo = g + custo_local
        if visitas is not None:
            visitas.append({"diretorio": pasta, "custo_local": custo_local, "g": custo})
        if encontrados:
            metricas.arquivos_encontrados += len(encontrados)
            contador += 1
            heapq.heappush(fronteira, (custo, contador, (pasta, encontrados, custo)))
            # Custos e h são não negativos: nenhum descendente sai do heap
            # antes deste objetivo, inserido primeiro também em caso de empate.
            # Outras pastas continuam concorrendo com a candidatura pelo heap.
            continue
        for item in itens:
            if item.is_dir(follow_symlinks=False):
                real = os.path.realpath(item.path)
                if real not in visitados:
                    visitados.add(real)
                    contador += 1
                    prioridade = custo + estimar(item.path) if estimar else custo
                    heapq.heappush(fronteira, (prioridade, contador, (item.path, None, custo)))
    return [], metricas
