"""Menu e CLI para buscas BFS/DFS/UCS/A* e gráficos opcionais de resultados."""

import argparse
import os
import time

from funcoes.bfs_dfs import buscar, mapear
from funcoes.metricas import PROTOCOLO_LOTE, medir_memoria, medir_tempo
from funcoes.ucs import ucs
from funcoes.astar import astar
from funcoes.heuristica import validar_alfa
from funcoes.pastas import (ARQUIVO_CONFIG, RAIZ_PADRAO, lembrar_pasta,
                            navegar_terminal, raiz_inicial, selecionar_pasta)
from funcoes.relatorio import criar_registro
from funcoes.interface import (apresentar_busca, apresentar_etapa, executar_menu,
                               exportar_arquivos as _exportar_graficos)


def _selecionar_busca(raiz, alvo, estrategia, modo, alfa, mapeamento):
    """Selecione a chamada sem iniciar a busca nem acessar a árvore."""
    if mapeamento:
        if modo != "nome" or alvo is not None:
            raise ValueError("Mapeamento global não recebe alvo nem lê conteúdo.")
        funcao, argumentos = mapear, (raiz, estrategia)
    elif estrategia == "astar":
        funcao, argumentos = astar, (raiz, alvo, modo, alfa)
    elif estrategia == "ucs":
        funcao, argumentos = ucs, (raiz, alvo, modo)
    else:
        funcao, argumentos = buscar, (raiz, alvo, estrategia, modo)
    return funcao, argumentos


def _medir_lote(chamadas, registrar_visitas, progresso=None):
    """Meça todos os tempos antes dos perfis, sempre com estado de busca novo."""
    amostras = []
    for indice, (funcao, argumentos) in enumerate(chamadas, 1):
        if progresso is not None:
            progresso("Tempo", indice, len(chamadas))
        visitas = [] if registrar_visitas else None
        resultado, tempo = medir_tempo(funcao, *argumentos, visitas=visitas)
        amostras.append((resultado, tempo, visitas))
    resultados = []
    for indice, (chamada, amostra) in enumerate(zip(chamadas, amostras), 1):
        funcao, argumentos = chamada
        (caminhos, metricas), tempo, visitas = amostra
        if progresso is not None:
            progresso("Memória", indice, len(chamadas))
        visitas_mem = [] if registrar_visitas else None
        (caminhos_mem, metricas_mem), memoria = medir_memoria(funcao, *argumentos, visitas=visitas_mem)
        if caminhos != caminhos_mem or metricas != metricas_mem or visitas != visitas_mem:
            raise RuntimeError("Resultados divergiram entre medições; a árvore pode ter mudado.")
        metricas.tempo_ms = tempo
        metricas.pico_mem_kb = memoria
        resultados.append((caminhos, metricas, visitas))
    return resultados


def executar(raiz, alvo, estrategia, modo="nome", alfa=1.0, *,
             mapeamento=False, visitas=None, progresso=None):
    """Execute duas buscas independentes e combine as medições, sem persistir."""
    chamada = _selecionar_busca(raiz, alvo, estrategia, modo, alfa, mapeamento)
    caminhos, metricas, rastro = _medir_lote([chamada], visitas is not None, progresso)[0]
    if visitas is not None:
        visitas[:] = rastro
    return caminhos, metricas


def comparar_conteudo(raiz, alvo="algoritmo", alfa=1.0):
    """Execute UCS/A* sequencialmente, com estados novos, sem gravar artefatos."""
    return executar_etapa(3, raiz, alvo, alfa)


def executar_etapa(etapa, raiz=RAIZ_PADRAO, alvo=None, alfa=1.0, *, progresso=None):
    """Execute a entrega específica, com registros auditáveis e sem gravar."""
    if type(etapa) is not int or etapa not in (1, 2, 3):
        raise ValueError("Etapa deve ser 1, 2 ou 3.")
    if etapa == 1 and alvo is not None:
        raise ValueError("Etapa 1 é mapeamento sem alvo.")
    alfa = validar_alfa(alfa)
    if etapa == 2 and alvo is None:
        alvo = "livro"
    if etapa == 3 and alvo is None:
        alvo = "algoritmo"
    algoritmos = {1: ("bfs", "dfs"), 2: ("bfs", "dfs", "ucs", "astar"), 3: ("ucs", "astar")}[etapa]
    modo = "conteudo" if etapa == 3 else "nome"
    experimento = f"{time.time_ns()}_{os.getpid()}"
    chamadas = [_selecionar_busca(raiz, alvo, algoritmo, modo, alfa, etapa == 1)
                for algoritmo in algoritmos]
    resultados = _medir_lote(chamadas, registrar_visitas=True, progresso=progresso)
    registros = []
    for algoritmo, (caminhos, metricas, visitas) in zip(algoritmos, resultados):
        registro = criar_registro(raiz, alvo, algoritmo, modo, caminhos, metricas, alfa,
                                  etapa=etapa, visitas=visitas)
        registro["experimento"] = experimento
        registro["protocolo_lote"] = PROTOCOLO_LOTE
        registros.append(registro)
    return registros


def _validar_opcoes(parser, args, etapa, estrategia):
    """Rejeite combinações inválidas antes de abrir diálogos ou salvar preferências."""
    if etapa is not None:
        modo = "conteudo" if etapa == 3 else "nome"
        if estrategia is not None or (args.modo is not None and args.modo != modo):
            parser.error("A etapa define seus algoritmos e modo; omita opções incompatíveis.")
        if etapa == 1 and (args.alvo is not None or args.alfa is not None):
            parser.error("Etapa 1 não recebe alvo nem alfa.")
    elif args.alfa is not None and estrategia is not None and estrategia != "astar":
        parser.error("--alfa se aplica somente ao algoritmo astar.")
    if args.alfa is not None:
        validar_alfa(args.alfa)


def main():
    """Leia argumentos; sem estratégia, ofereça o menu interativo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", help="Pasta inicial; padrão da CLI: ./docencia/fontes")
    selecao = parser.add_mutually_exclusive_group()
    selecao.add_argument("--selecionar-pasta", action="store_true", help="Abrir o seletor de pastas do sistema")
    selecao.add_argument("--navegar", action="store_true", help="Escolher pasta/arquivo pelo terminal")
    parser.add_argument("--config", default=ARQUIVO_CONFIG, help="JSON local da última pasta selecionada")
    parser.add_argument("--alvo", help="Trecho do nome/conteúdo; use .pdf para localizar PDFs por nome")
    parser.add_argument("--modo", choices=("nome", "conteudo"),
                        help="nome: qualquer extensão; conteudo: textos e PDF com pypdf (sem Office/OCR)")
    parser.add_argument("--algoritmo", choices=("bfs", "dfs", "ucs", "astar"))
    parser.add_argument("--alfa", type=float, help="Peso finito >= 0 da heurística A* (padrão: 1)")
    parser.add_argument("--resultados", default="resultados", help="Pasta dos JSONs (padrão: resultados)")
    parser.add_argument("--sem-salvar", action="store_true", help="Execute sem gravar JSON")
    entregas = parser.add_mutually_exclusive_group()
    entregas.add_argument("--comparar", action="store_true", help="Atalho da etapa 3: UCS/A* por conteúdo")
    entregas.add_argument("--etapa", type=int, choices=(1, 2, 3),
                          help="1: mapeamento BFS/DFS; 2: alvo no nome; 3: conteúdo UCS/A*")
    entregas.add_argument("--graficos", nargs="+", metavar="JSON_OU_PASTA",
                          help="Exportar gráficos de resultados; requer Matplotlib opcional")
    parser.add_argument("--saida-graficos", help="Diretório dos PNGs (padrão: resultados/graficos)")
    args = parser.parse_args()
    try:
        if args.graficos is not None:
            if (any(v is not None for v in (args.algoritmo, args.raiz, args.alvo, args.modo, args.alfa))
                    or args.selecionar_pasta or args.navegar or args.sem_salvar):
                parser.error("--graficos usa JSONs existentes; omita opções de busca e --sem-salvar.")
            _exportar_graficos(args.graficos, args.saida_graficos or os.path.join(args.resultados, "graficos"))
            return
        if args.saida_graficos is not None:
            parser.error("--saida-graficos exige --graficos.")
        etapa = 3 if args.comparar else args.etapa
        estrategia = args.algoritmo
        _validar_opcoes(parser, args, etapa, estrategia)
        interativo = etapa is None and estrategia is None
        raiz = raiz_inicial(args.raiz, args.config,
                            usar_ultima=interativo or args.selecionar_pasta or args.navegar)
        sugestao = None
        lembrar = args.raiz is not None
        if args.selecionar_pasta or args.navegar:
            escolha = (selecionar_pasta(raiz) if args.selecionar_pasta
                       else navegar_terminal(raiz))
            if escolha is None:
                print("Seleção cancelada.")
                return
            raiz, sugestao = escolha
            raiz = lembrar_pasta(raiz, args.config)
            lembrar = False
        if interativo:
            if lembrar:
                raiz = lembrar_pasta(raiz, args.config)
            executar_menu(args, raiz, sugestao, executar_etapa, executar)
            return
        if lembrar:
            raiz = lembrar_pasta(raiz, args.config)
        if etapa is not None:
            alfa = args.alfa if args.alfa is not None else 1.0
            alvo = args.alvo if args.alvo is not None else (sugestao if etapa == 2 else None)
            registros = executar_etapa(etapa, raiz, alvo, alfa)
            apresentar_etapa(registros, etapa, alvo, args)
            return
        modo = args.modo or "nome"
        if args.alvo is not None:
            alvo = args.alvo
        else:
            padrao = sugestao if modo == "nome" else None
            alvo = input(f"Termo procurado [{padrao}]: " if padrao else "Termo procurado: ").strip()
            alvo = alvo or padrao or ""
        alfa = args.alfa if args.alfa is not None else 1.0
        caminhos, metricas = executar(raiz, alvo, estrategia, modo, alfa)
        apresentar_busca(raiz, alvo, estrategia, modo, alfa, caminhos, metricas, args)
    except (OSError, ValueError, RuntimeError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, "\nEntrada interrompida.\n")


if __name__ == "__main__":
    main()
