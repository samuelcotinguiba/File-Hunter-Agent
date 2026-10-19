"""Busca uniforme por nome com custos conhecidos apenas após a expansão."""

import heapq
import os

from .listagem import listar_dir
from .metricas import Metricas


def ucs(raiz, alvo):
    """Retorne (arquivos da pasta objetivo de menor custo, métricas).

    Pastas pendentes entram com o custo do pai, um limite inferior. Expandir
    revela len(itens); a candidatura a objetivo volta ao heap com o custo exato.
    Assim não é necessário listar antecipadamente nem aceitar um alvo caro
    enquanto há uma pasta pendente que pode produzir um alvo mais barato.
    """
    if not alvo:
        raise ValueError("O alvo não pode ser vazio.")
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
        custo = prioridade + len(itens)
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
                    subpastas.append(item.path)
        if encontrados:
            metricas.arquivos_encontrados += len(encontrados)
            contador += 1
            heapq.heappush(fronteira, (custo, contador, (pasta, encontrados)))
        for subpasta in subpastas:
            contador += 1
            heapq.heappush(fronteira, (custo, contador, (subpasta, None)))
    return [], metricas
