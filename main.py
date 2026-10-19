"""Menu e CLI para buscas BFS/DFS/UCS/A* por nome ou conteúdo."""

import argparse

from funcoes.bfs_dfs import buscar
from funcoes.metricas import medir_memoria, medir_tempo, metricas_principais
from funcoes.ucs import ucs
from funcoes.astar import astar
from funcoes.heuristica import validar_alfa
from funcoes.relatorio import criar_registro, gerar_tabela_comparativa, salvar_execucao, salvar_registro


def executar(raiz, alvo, estrategia, modo="nome", alfa=1.0):
    """Execute duas buscas independentes e combine as medições."""
    if estrategia == "astar":
        funcao, argumentos = astar, (raiz, alvo, modo, alfa)
    elif estrategia == "ucs":
        funcao, argumentos = ucs, (raiz, alvo, modo)
    else:
        funcao, argumentos = buscar, (raiz, alvo, estrategia, modo)
    (caminhos, metricas), tempo = medir_tempo(funcao, *argumentos)
    (caminhos_mem, metricas_mem), memoria = medir_memoria(funcao, *argumentos)
    if caminhos != caminhos_mem or metricas != metricas_mem:
        raise RuntimeError("Resultados divergiram entre medições; a árvore pode ter mudado.")
    metricas.tempo_ms = tempo
    metricas.pico_mem_kb = memoria
    return caminhos, metricas


def comparar_conteudo(raiz, alvo="algoritmo", alfa=1.0):
    """Execute UCS/A* sequencialmente, com estados novos, sem gravar artefatos."""
    alfa = validar_alfa(alfa)
    registros = []
    for algoritmo in ("ucs", "astar"):
        caminhos, metricas = executar(raiz, alvo, algoritmo, "conteudo", alfa)
        registros.append(criar_registro(raiz, alvo, algoritmo, "conteudo", caminhos, metricas, alfa))
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
    parser.add_argument("--comparar", action="store_true", help="Compare UCS e A* no conteúdo; alvo padrão: algoritmo")
    args = parser.parse_args()
    try:
        if args.comparar:
            if args.algoritmo is not None or args.modo == "nome":
                parser.error("--comparar usa UCS e A* com modo conteudo; omita --algoritmo e --modo nome.")
            alvo = args.alvo if args.alvo is not None else "algoritmo"
            alfa = args.alfa if args.alfa is not None else 1.0
            registros = comparar_conteudo(args.raiz, alvo, alfa)
            texto = gerar_tabela_comparativa(registros, alvo)
            arquivos = []
            if not args.sem_salvar:
                arquivos = [salvar_registro(r, args.resultados) for r in registros]
            print(texto)
            for arquivo in arquivos:
                print(f"JSON salvo em {arquivo}")
            return
        estrategia = args.algoritmo
        if estrategia is None:
            print("File Hunter Agent\n1. BFS\n2. DFS\n3. UCS\n4. A*\n0. Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                return
            if opcao not in ("1", "2", "3", "4"):
                parser.error("Opção inválida; escolha 1, 2, 3, 4 ou 0.")
            estrategia = {"1": "bfs", "2": "dfs", "3": "ucs", "4": "astar"}[opcao]
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
