"""Tabelas compactas e caminhos legíveis no terminal, sem dependências externas."""

import os
import textwrap

from .metricas import ROTULOS_PRINCIPAIS
from .relatorio import caminho_relativo, validar_registro


_NOMES = {"bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "astar": "A*"}


def largura_terminal():
    """Use a largura disponível, com limite de leitura e fallback para saída redirecionada."""
    try:
        largura = os.get_terminal_size().columns
    except OSError:
        largura = 80
    return max(20, min(largura, 120))


def _quebrar(texto, largura):
    partes = str(texto).splitlines() or [""]
    return [linha for parte in partes for linha in
            (textwrap.wrap(parte, width=largura, break_on_hyphens=False) or [""])]


def _tabela(cabecalho, linhas, largura):
    """Alinhe números à direita e quebre células longas sem remover seu conteúdo."""
    dados = [list(map(str, cabecalho)), *[list(map(str, linha)) for linha in linhas]]
    tamanhos = [max(len(celula) for linha in dados for celula in linha[i].splitlines() or [""])
                for i in range(len(cabecalho))]
    while sum(tamanhos) + 3 * len(tamanhos) + 1 > largura:
        indice = max(range(len(tamanhos)), key=tamanhos.__getitem__)
        if tamanhos[indice] <= 1:
            break
        tamanhos[indice] -= 1

    def borda(esquerda, meio, direita):
        return esquerda + meio.join("─" * (t + 2) for t in tamanhos) + direita

    resultado = [borda("┌", "┬", "┐")]
    for numero, linha in enumerate(dados):
        celulas = [_quebrar(celula, tamanho) for celula, tamanho in zip(linha, tamanhos)]
        for indice in range(max(map(len, celulas))):
            valores = [celula[indice] if indice < len(celula) else "" for celula in celulas]
            resultado.append("│ " + " │ ".join(
                valor.ljust(tamanho) if coluna == 0 else valor.rjust(tamanho)
                for coluna, (valor, tamanho) in enumerate(zip(valores, tamanhos))) + " │")
        if numero == 0:
            resultado.append(borda("├", "┼", "┤"))
    resultado.append(borda("└", "┴", "┘"))
    return "\n".join(resultado)


def _numero(valor):
    if type(valor) is int:
        return f"{valor:,}".replace(",", ".")
    return f"{valor:,.3f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _caminho(caminho, largura, prefixo="  "):
    """Prefira quebrar entre diretórios, mantendo o nome do arquivo inteiro quando couber."""
    linhas = []
    atual = prefixo
    recuo = " " * len(prefixo)
    partes = caminho.split("/")
    for indice, parte in enumerate(partes):
        trecho = parte + ("/" if indice < len(partes) - 1 else "")
        if len(atual) + len(trecho) > largura and len(atual) > len(prefixo):
            linhas.append(atual)
            atual = recuo
        while len(atual) + len(trecho) > largura:
            disponivel = largura - len(atual)
            linhas.append(atual + trecho[:disponivel])
            trecho = trecho[disponivel:]
            atual = recuo
        atual += trecho
    return "\n".join([*linhas, atual])


def resumo_etapa(registros, etapa, *, largura=None):
    """Mostre métricas uma vez e separe caminhos, ordem de descoberta e interpretação."""
    if type(etapa) is not int or etapa not in (1, 2, 3):
        raise ValueError("Etapa deve ser 1, 2 ou 3.")
    registros = sorted((validar_registro(r) for r in registros),
                       key=lambda r: tuple(_NOMES).index(r["parametros"]["algoritmo"]))
    if not registros or any(r["parametros"].get("etapa") != etapa for r in registros):
        raise ValueError("O resumo deve receber registros da etapa solicitada.")
    largura = largura_terminal() if largura is None else max(20, largura)
    titulo = {1: "Mapeamento de arquivos", 2: "Busca por nome", 3: "Busca por conteúdo"}[etapa]
    linhas = ["", f"ETAPA {etapa} — {titulo}", ""]
    if etapa != 1:
        linhas.extend(_quebrar("Palavra: " + registros[0]["parametros"]["alvo"], largura))
        linhas.append("")
    campos = [(ROTULOS_PRINCIPAIS[0], "pastas_abertas"),
              (ROTULOS_PRINCIPAIS[1], "itens_examinados"),
              (ROTULOS_PRINCIPAIS[2], "arquivos_lidos")]
    if etapa == 1:
        campos.insert(1, ("Total de Arquivos Encontrados", "arquivos_encontrados"))
    unidade = "bytes" if etapa == 3 else "itens"
    campos.extend([(f"{ROTULOS_PRINCIPAIS[3]} ({unidade})", "custo_g"),
                   (ROTULOS_PRINCIPAIS[4].replace(", tracemalloc", ""), "pico_mem_kb"),
                   (ROTULOS_PRINCIPAIS[5], "tempo_ms")])
    if etapa == 3:
        campos.insert(4, ("Custo Total f(n) (bytes)", "custo_g"))
    quantidade = 4 if largura >= 78 else (2 if largura >= 52 else 1)
    for inicio in range(0, len(registros), quantidade):
        grupo = registros[inicio:inicio + quantidade]
        valores = [(rotulo, *["—" if campo == "custo_g" and (etapa == 1 or not r["encontrados"])
                             else _numero(r["metricas"][campo]) for r in grupo])
                   for rotulo, campo in campos]
        linhas.extend([_tabela(["Métrica", *[_NOMES[r["parametros"]["algoritmo"]] for r in grupo]],
                               valores, largura), ""])
    linhas.extend(_quebrar("Tempo e memória medidos separadamente; pico Python via tracemalloc.", largura))
    if etapa == 1:
        linhas.extend(["g(n): não se aplica ao mapeamento.", "", "Ordem de descoberta — primeiros 10 arquivos"])
        for registro in registros:
            linhas.extend(["", _NOMES[registro["parametros"]["algoritmo"]]])
            for indice, caminho in enumerate(registro["encontrados"][:10], 1):
                prefixo = f"  {indice:>2}. "
                linhas.append(_caminho(caminho_relativo(registro, caminho), largura, prefixo))
            if not registro["encontrados"]:
                linhas.append("  Nenhum arquivo encontrado.")
    else:
        linhas.extend(["", "Caminhos encontrados"])
        grupos = {}
        for registro in registros:
            caminhos = tuple(caminho_relativo(registro, c) for c in registro["encontrados"])
            grupos.setdefault(caminhos, []).append(_NOMES[registro["parametros"]["algoritmo"]])
        for caminhos, nomes in grupos.items():
            linhas.extend(["", " / ".join(nomes)])
            for caminho in caminhos or ("Não encontrado.",):
                linhas.append(_caminho(caminho, largura))
        pares = {r["parametros"]["algoritmo"]: r for r in registros}
        if "ucs" in pares and "astar" in pares:
            diferencas = []
            for campo, nome in (("pastas_abertas", "pastas abertas"), ("arquivos_lidos", "arquivos lidos")):
                if campo == "arquivos_lidos" and etapa == 2:
                    continue
                delta = pares["ucs"]["metricas"][campo] - pares["astar"]["metricas"][campo]
                diferencas.append(f"{nome}: mesmo total" if delta == 0 else
                                  f"{nome}: {_numero(abs(delta))} a {'menos' if delta > 0 else 'mais'}")
            linhas.extend(["", *_quebrar("A* em relação ao UCS — " + "; ".join(diferencas) + ".", largura)])
        if etapa == 3:
            pesos = ", ".join(f'{r["parametros"]["alfa"]:g}'.replace(".", ",") for r in registros
                              if r["parametros"]["algoritmo"] == "astar")
            peso = f"; alfa={pesos}" if pesos else ""
            linhas.extend(["", *_quebrar(f"h(n) = alfa × (1 − Jaccard de bigramas){peso}.", largura),
                           *_quebrar("No objetivo: h=0 e f=g. A* não garante ótimo ou economia.", largura)])
    return "\n".join(parte for bloco in linhas for linha in bloco.split("\n") for parte in
                     (_quebrar(linha, largura) if len(linha) > largura else [linha]))
