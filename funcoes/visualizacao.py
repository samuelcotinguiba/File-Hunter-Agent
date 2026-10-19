"""Gráficos opcionais de JSONs medidos, sem executar buscas ou abrir janelas."""

import argparse
import os
import time

from .metricas import ROTULOS_PRINCIPAIS
from .relatorio import carregar_resultados, validar_registro


ORDEM = ("bfs", "dfs", "ucs", "astar")
NOMES = {"bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "astar": "A*"}
CORES = {"bfs": "#2563eb", "dfs": "#9333ea", "ucs": "#c2410c", "astar": "#047857"}
CAMPOS = ("pastas_abertas", "itens_examinados", "arquivos_lidos", "custo_g",
          "pico_mem_kb", "tempo_ms")


def verificar_dependencia():
    """Importe Matplotlib somente ao solicitar gráficos, com orientação de instalação."""
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
    except ImportError as erro:
        raise RuntimeError(
            "Gráficos requerem a dependência opcional Matplotlib. "
            "Instale no mesmo ambiente: python -m pip install -r requirements.txt"
        ) from erro
    return Figure, FigureCanvasAgg


def agrupar_resultados(registros):
    """Separe experimentos/políticas e rejeite algoritmos duplicados no mesmo grupo."""
    grupos = {}
    for registro in registros:
        validar_registro(registro)
        p = registro["parametros"]
        extensoes = p.get("extensoes_texto")
        chave = (os.path.normcase(os.path.normpath(p["raiz"])), p.get("etapa"),
                 p.get("escopo", "objetivo"), p["modo"], (p.get("alvo") or "").casefold(),
                 tuple(sorted(extensoes)) if extensoes is not None else None,
                 p.get("extrator_pdf"), registro.get("experimento"),
                 registro.get("protocolo_lote"), "medicao" in registro)
        grupo = grupos.setdefault(chave, {})
        algoritmo = p["algoritmo"]
        if algoritmo in grupo:
            raise ValueError(
                f"Mais de uma execução {NOMES[algoritmo]} no mesmo grupo; "
                "selecione um JSON por algoritmo e experimento."
            )
        grupo[algoritmo] = registro
    if not grupos:
        raise ValueError("Nenhuma execução para visualizar.")
    return [[grupo[a] for a in ORDEM if a in grupo] for grupo in grupos.values()]


def _figura(grupo, Figure, FigureCanvasAgg):
    """Monte seis painéis com unidades próprias e custo ausente explicitamente marcado."""
    from matplotlib.ticker import MaxNLocator

    figura = Figure(figsize=(12, 9), dpi=140, layout="constrained")
    FigureCanvasAgg(figura)
    p = grupo[0]["parametros"]
    mapeamento = p.get("escopo") == "mapeamento"
    modo = "conteúdo" if p["modo"] == "conteudo" else "nome"
    titulo = "Mapeamento global" if mapeamento else f'Busca por {modo}: {p["alvo"]}'
    experimento = grupo[0].get("experimento", "não registrado")
    figura.suptitle(f"File Hunter Agent — {titulo}\nRaiz: {p['raiz']}\nExperimento: {experimento}",
                    fontsize=10, wrap=True, parse_math=False)
    nomes = [NOMES[r["parametros"]["algoritmo"]] for r in grupo]
    cores = [CORES[r["parametros"]["algoritmo"]] for r in grupo]
    for eixo, campo, rotulo in zip(figura.subplots(2, 3).flat, CAMPOS, ROTULOS_PRINCIPAIS):
        titulo_painel = rotulo.replace(" — ", "\n")
        if campo == "custo_g":
            titulo_painel += " (bytes)" if p["modo"] == "conteudo" else " (itens)"
        eixo.set_title(titulo_painel, fontsize=10)
        eixo.set_xticks(range(len(grupo)), nomes)
        eixo.set_xlim(-0.5, len(grupo) - 0.5)
        eixo.grid(axis="y", alpha=0.25)
        eixo.set_axisbelow(True)
        for i, (registro, cor) in enumerate(zip(grupo, cores)):
            if campo == "custo_g" and (mapeamento or not registro["encontrados"]):
                mensagem = "Não se aplica" if mapeamento else "Não encontrado"
                eixo.text(i, 0.08, mensagem, ha="center", fontsize=8,
                          transform=eixo.get_xaxis_transform())
                continue
            valor = registro["metricas"][campo]
            barra = eixo.bar(i, valor, color=cor, width=0.6)
            texto = f"{valor:.3f}" if campo in ("tempo_ms", "pico_mem_kb") else str(valor)
            eixo.bar_label(barra, labels=[texto], padding=3, fontsize=8)
        eixo.margins(y=0.2)
        eixo.set_ylim(bottom=0)
        if not eixo.patches:
            eixo.set_yticks([])
        elif all(barra.get_height() == 0 for barra in eixo.patches):
            eixo.set_ylim(0, 1)
        if eixo.patches and campo not in ("tempo_ms", "pico_mem_kb"):
            eixo.yaxis.set_major_locator(MaxNLocator(integer=True))
    pesos = "; ".join(f'A*: alfa={r["parametros"]["alfa"]:g}' for r in grupo
                      if r["parametros"]["algoritmo"] == "astar")
    figura.supxlabel(
        "Tempo e memória medidos em execuções separadas; pico de alocações Python, não RSS.\n"
        + (pesos + ". Heurística sem garantia de ótimo ou economia." if pesos else ""),
        fontsize=9)
    return figura


def gerar_graficos(registros, diretorio="resultados/graficos"):
    """Exporte um PNG exclusivo por grupo, preservando os registros de entrada."""
    grupos = agrupar_resultados(registros)
    Figure, FigureCanvasAgg = verificar_dependencia()
    diretorio = os.path.abspath(diretorio)
    os.makedirs(diretorio, exist_ok=True)
    caminhos = []
    for grupo in grupos:
        figura = _figura(grupo, Figure, FigureCanvasAgg)
        base = f"grafico_{time.time_ns()}_{os.getpid()}"
        contador = 0
        try:
            while True:
                caminho = os.path.join(diretorio, f"{base}_{contador}.png")
                try:
                    arquivo = open(caminho, "xb")
                    break
                except FileExistsError:
                    contador += 1
            try:
                with arquivo:
                    figura.savefig(arquivo, format="png")
            except BaseException:
                os.unlink(caminho)
                raise
            caminhos.append(caminho)
        finally:
            figura.clear()
    return caminhos


def main():
    """Converta JSONs em gráficos PNG, sem exigir interface gráfica."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entradas", nargs="+", help="Arquivos JSON ou diretórios de resultados")
    parser.add_argument("--saida", default="resultados/graficos", help="Diretório dos gráficos PNG")
    args = parser.parse_args()
    try:
        for caminho in gerar_graficos(carregar_resultados(args.entradas), args.saida):
            print(f"Gráfico salvo em {caminho}")
    except (OSError, ValueError, RuntimeError) as erro:
        parser.exit(1, f"Erro: {erro}\n")


if __name__ == "__main__":
    main()
