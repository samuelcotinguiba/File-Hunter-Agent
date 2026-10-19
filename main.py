"""Menu e CLI para buscas BFS/DFS/UCS por nome de arquivo."""

import argparse

from funcoes.bfs_dfs import buscar
from funcoes.metricas import medir_memoria, medir_tempo
from funcoes.ucs import ucs


def executar(raiz, alvo, estrategia):
    """Execute duas buscas independentes e combine as medições."""
    funcao = ucs if estrategia == "ucs" else buscar
    argumentos = (raiz, alvo) if estrategia == "ucs" else (raiz, alvo, estrategia)
    (caminhos, metricas), tempo = medir_tempo(funcao, *argumentos)
    (caminhos_mem, metricas_mem), memoria = medir_memoria(funcao, *argumentos)
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
    parser.add_argument("--algoritmo", choices=("bfs", "dfs", "ucs"))
    args = parser.parse_args()
    try:
        estrategia = args.algoritmo
        if estrategia is None:
            print("File Hunter Agent — busca por nome\n1. BFS\n2. DFS\n3. UCS\n0. Sair")
            opcao = input("Opção: ").strip()
            if opcao == "0":
                return
            if opcao not in ("1", "2", "3"):
                parser.error("Opção inválida; escolha 1, 2, 3 ou 0.")
            estrategia = {"1": "bfs", "2": "dfs", "3": "ucs"}[opcao]
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
