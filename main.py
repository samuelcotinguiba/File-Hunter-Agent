"""Menu e CLI para buscas BFS/DFS por nome de arquivo."""

import argparse

from funcoes.bfs_dfs import buscar
from funcoes.metricas import medir_memoria, medir_tempo


def executar(raiz, alvo, estrategia):
    """Execute duas buscas independentes e combine as medições."""
    (caminhos, metricas), tempo = medir_tempo(buscar, raiz, alvo, estrategia)
    (caminhos_mem, metricas_mem), memoria = medir_memoria(buscar, raiz, alvo, estrategia)
    if caminhos != caminhos_mem or metricas != metricas_mem:
        raise RuntimeError("A árvore mudou entre as medições; repita a execução.")
    metricas.tempo_ms = tempo
    metricas.pico_mem_kb = memoria
    return caminhos, metricas


def main():
    """Leia argumentos; sem estratégia, ofereça o menu interativo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default="./docencia/fontes")
    parser.add_argument("--alvo", help="Trecho do nome, sem distinguir maiúsculas")
    parser.add_argument("--algoritmo", choices=("bfs", "dfs"))
    args = parser.parse_args()
    try:
        estrategia = args.algoritmo
        if estrategia is None:
            print("File Hunter Agent — busca por nome\n1. BFS\n2. DFS\n0. Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                return
            if opcao not in ("1", "2"):
                parser.error("Opção inválida; escolha 1, 2 ou 0.")
            estrategia = {"1": "bfs", "2": "dfs"}[opcao]
        alvo = args.alvo if args.alvo is not None else input("Nome procurado: ").strip()
        caminhos, metricas = executar(args.raiz, alvo, estrategia)
    except (OSError, ValueError, RuntimeError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, "\nEntrada interrompida.\n")
    print(f"\nBusca: {estrategia.upper()}")
    print("\n".join(caminhos) if caminhos else "Nenhum arquivo encontrado.")
    for campo, valor in vars(metricas).items():
        print(f"{campo}: {valor:.3f}" if isinstance(valor, float)
              else f"{campo}: {valor}")


if __name__ == "__main__":
    main()
