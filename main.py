"""Menu e CLI para buscas BFS/DFS/UCS/A* por nome ou conteúdo."""

import argparse
import os
import time

from funcoes.bfs_dfs import buscar, mapear
from funcoes.metricas import (PROTOCOLO_LOTE, medir_memoria, medir_tempo,
                              metricas_principais)
from funcoes.ucs import ucs
from funcoes.astar import astar
from funcoes.heuristica import validar_alfa
from funcoes.relatorio import (criar_registro, gerar_relatorio_etapa,
                               salvar_execucao, salvar_registro, salvar_markdown)


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


def _medir_lote(chamadas, registrar_visitas):
    """Meça todos os tempos antes dos perfis, sempre com estado de busca novo."""
    amostras = []
    for funcao, argumentos in chamadas:
        visitas = [] if registrar_visitas else None
        resultado, tempo = medir_tempo(funcao, *argumentos, visitas=visitas)
        amostras.append((resultado, tempo, visitas))
    resultados = []
    for (funcao, argumentos), ((caminhos, metricas), tempo, visitas) in zip(chamadas, amostras):
        visitas_mem = [] if registrar_visitas else None
        (caminhos_mem, metricas_mem), memoria = medir_memoria(funcao, *argumentos, visitas=visitas_mem)
        if caminhos != caminhos_mem or metricas != metricas_mem or visitas != visitas_mem:
            raise RuntimeError("Resultados divergiram entre medições; a árvore pode ter mudado.")
        metricas.tempo_ms = tempo
        metricas.pico_mem_kb = memoria
        resultados.append((caminhos, metricas, visitas))
    return resultados


def executar(raiz, alvo, estrategia, modo="nome", alfa=1.0, *, mapeamento=False, visitas=None):
    """Execute duas buscas independentes e combine as medições, sem persistir."""
    chamada = _selecionar_busca(raiz, alvo, estrategia, modo, alfa, mapeamento)
    caminhos, metricas, rastro = _medir_lote([chamada], visitas is not None)[0]
    if visitas is not None:
        visitas[:] = rastro
    return caminhos, metricas


def comparar_conteudo(raiz, alvo="algoritmo", alfa=1.0):
    """Execute UCS/A* sequencialmente, com estados novos, sem gravar artefatos."""
    return executar_etapa(3, raiz, alvo, alfa)


def executar_etapa(etapa, raiz="./docencia/fontes", alvo=None, alfa=1.0):
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
    resultados = _medir_lote(chamadas, registrar_visitas=True)
    registros = []
    for algoritmo, (caminhos, metricas, visitas) in zip(algoritmos, resultados):
        registro = criar_registro(raiz, alvo, algoritmo, modo, caminhos, metricas, alfa,
                                  etapa=etapa, visitas=visitas)
        registro["experimento"] = experimento
        registro["protocolo_lote"] = PROTOCOLO_LOTE
        registros.append(registro)
    return registros


def main():
    """Leia argumentos; sem estratégia, ofereça o menu interativo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default="./docencia/fontes", help="Pasta inicial; percorre subpastas")
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
    args = parser.parse_args()
    try:
        etapa = 3 if args.comparar else args.etapa
        estrategia = args.algoritmo
        if etapa is None and estrategia is None:
            print("File Hunter Agent\n1. BFS\n2. DFS\n3. UCS\n4. A*"
                  "\n5. Etapa 1 — Mapeamento BFS/DFS\n6. Etapa 2 — Comparar por nome"
                  "\n7. Etapa 3 — Comparar por conteúdo\n0. Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                return
            if opcao not in ("1", "2", "3", "4", "5", "6", "7"):
                parser.error("Opção inválida; escolha de 0 a 7.")
            if opcao in ("5", "6", "7"):
                etapa = {"5": 1, "6": 2, "7": 3}[opcao]
            else:
                estrategia = {"1": "bfs", "2": "dfs", "3": "ucs", "4": "astar"}[opcao]
        if etapa is not None:
            modo_etapa = "conteudo" if etapa == 3 else "nome"
            if estrategia is not None or (args.modo is not None and args.modo != modo_etapa):
                parser.error("A etapa define seus algoritmos e modo; omita opções incompatíveis.")
            if etapa == 1 and (args.alvo is not None or args.alfa is not None):
                parser.error("Etapa 1 não recebe alvo nem alfa.")
            alfa = args.alfa if args.alfa is not None else 1.0
            registros = executar_etapa(etapa, args.raiz, args.alvo, alfa)
            arquivos = []
            if not args.sem_salvar:
                for registro in registros:
                    caminho_json = salvar_registro(registro, args.resultados)
                    registro["origem_json"] = caminho_json
                    arquivos.append(caminho_json)
            texto = gerar_relatorio_etapa(registros, etapa, args.alvo)
            print(texto)
            for arquivo in arquivos:
                print(f"JSON salvo em {arquivo}")
            if not args.sem_salvar:
                caminho_md = salvar_markdown(texto, os.path.join(args.resultados, f"etapa_{etapa}.md"))
                print(f"Relatório salvo em {caminho_md}")
            return
        if args.alfa is not None and estrategia != "astar":
            parser.error("--alfa se aplica somente ao algoritmo astar.")
        modo = args.modo
        if modo is None:
            if args.algoritmo is None:
                opcao_modo = input("Modo: 1. Nome (qualquer tipo)  2. Conteúdo (texto/PDF) [1]: ").strip()
                if opcao_modo not in ("", "1", "2"):
                    parser.error("Modo inválido; escolha 1 ou 2.")
                modo = "conteudo" if opcao_modo == "2" else "nome"
            else:
                modo = "nome"
        alvo = args.alvo if args.alvo is not None else input("Termo procurado: ").strip()
        alfa = args.alfa if args.alfa is not None else 1.0
        caminhos, metricas = executar(args.raiz, alvo, estrategia, modo, alfa)
        arquivo_json = None
        if not args.sem_salvar:
            arquivo_json = salvar_execucao(args.raiz, alvo, estrategia, modo,
                                          caminhos, metricas, alfa, args.resultados)
    except (OSError, ValueError, RuntimeError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, "\nEntrada interrompida.\n")
    print(f"\nBusca: {estrategia.upper()} | modo: {modo}")
    if estrategia == "astar":
        print(f"alfa: {alfa:g}; heurística não admissível, sem garantia de caminho ótimo.")
    print("\n".join(caminhos) if caminhos else "Nenhum arquivo encontrado.")
    for campo, valor in metricas_principais(metricas, modo).items():
        print(f"{campo}: {valor:.3f}" if isinstance(valor, float)
              else f"{campo}: {valor}")
    print(f"Arquivos encontrados: {metricas.arquivos_encontrados}")
    if arquivo_json:
        print(f"JSON salvo em {arquivo_json}")


if __name__ == "__main__":
    main()
