"""Menu e CLI para buscas BFS/DFS/UCS por nome ou conteúdo."""

import argparse

from funcoes.bfs_dfs import buscar
from funcoes.metricas import medir_memoria, medir_tempo
from funcoes.ucs import ucs


def executar(raiz, alvo, estrategia, modo="nome"):
    """Execute duas buscas independentes e combine as medições."""
    funcao = ucs if estrategia == "ucs" else buscar
    argumentos = ((raiz, alvo, modo) if estrategia == "ucs"
                  else (raiz, alvo, estrategia, modo))
    (caminhos, metricas), tempo = medir_tempo(funcao, *argumentos)
    (caminhos_mem, metricas_mem), memoria = medir_memoria(funcao, *argumentos)
    if caminhos != caminhos_mem or metricas != metricas_mem:
        raise RuntimeError("Resultados divergiram entre medições; a árvore pode ter mudado.")
    metricas.tempo_ms = tempo
    metricas.pico_mem_kb = memoria
    return caminhos, metricas


def main():
    """Leia argumentos; sem estratégia, ofereça o menu interativo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default="./docencia/fontes")
    parser.add_argument("--alvo", help="Termo procurado, sem distinguir maiúsculas")
    parser.add_argument("--modo", choices=("nome", "conteudo"))
    parser.add_argument("--algoritmo", choices=("bfs", "dfs", "ucs"))
    args = parser.parse_args()
    try:
        estrategia = args.algoritmo
        if estrategia is None:
            print("File Hunter Agent\n1. BFS\n2. DFS\n3. UCS\n0. Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                return
            if opcao not in ("1", "2", "3"):
                parser.error("Opção inválida; escolha 1, 2, 3 ou 0.")
            estrategia = {"1": "bfs", "2": "dfs", "3": "ucs"}[opcao]
        modo = args.modo
        if modo is None:
            if args.algoritmo is None:
                opcao_modo = input("Modo: 1. Nome  2. Conteúdo [1]: ").strip()
                if opcao_modo not in ("", "1", "2"):
                    parser.error("Modo inválido; escolha 1 ou 2.")
                modo = "conteudo" if opcao_modo == "2" else "nome"
            else:
                modo = "nome"
        alvo = args.alvo if args.alvo is not None else input("Termo procurado: ").strip()
        caminhos, metricas = executar(args.raiz, alvo, estrategia, modo)
    except (OSError, ValueError, RuntimeError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, "\nEntrada interrompida.\n")
    print(f"\nBusca: {estrategia.upper()} | modo: {modo}")
    print("\n".join(caminhos) if caminhos else "Nenhum arquivo encontrado.")
    for campo, valor in vars(metricas).items():
        print(f"{campo}: {valor:.3f}" if isinstance(valor, float)
              else f"{campo}: {valor}")


if __name__ == "__main__":
    main()
