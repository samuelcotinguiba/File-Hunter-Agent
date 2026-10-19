"""Verificações executáveis com python3 -m tests.test_buscas."""

import os

from funcoes.bfs_dfs import buscar
from main import executar


def main():
    """Verifique ordem, custo por caminho, descoberta e ciclos."""
    raiz = os.path.join(os.getcwd(), "tests", "temporario_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        os.makedirs(os.path.join(raiz, "a", "profunda"))
        os.mkdir(os.path.join(raiz, "b"))
        for nome in ("a/profunda/ALVO.txt", "b/alvo.md", "b/ALVO.txt"):
            with open(os.path.join(raiz, nome), "w", encoding="utf-8") as arquivo:
                arquivo.write("Texto de teste")
        os.symlink(raiz, os.path.join(raiz, "a", "ciclo"))
        caminhos, m = buscar(raiz, "AlVo", "bfs")
        assert caminhos == [os.path.join(raiz, "b", "ALVO.txt")]
        assert (m.pastas_abertas, m.itens_examinados, m.custo_g) == (3, 5, 4)
        assert m.arquivos_encontrados == 2 and m.arquivos_lidos == 0
        caminhos, m = buscar(raiz, "AlVo", "dfs")
        assert caminhos == [os.path.join(raiz, "a", "profunda", "ALVO.txt")]
        assert (m.pastas_abertas, m.itens_examinados, m.custo_g) == (3, 4, 4)
        for estrategia in ("bfs", "dfs"):
            caminhos, m = buscar(raiz, "ausente", estrategia)
            assert caminhos == []
            assert (m.pastas_abertas, m.itens_examinados, m.custo_g) == (4, 6, 0)
            _, medidos = executar(raiz, "alvo", estrategia)
            assert medidos.tempo_ms >= 0 and medidos.pico_mem_kb > 0
        for alvo, estrategia in (("", "bfs"), ("alvo", "invalida")):
            try:
                buscar(raiz, alvo, estrategia)
            except ValueError:
                pass
            else:
                raise AssertionError("Entrada inválida aceita")
        with open(os.path.join(raiz, "alvo_raiz.txt"), "w") as arquivo:
            arquivo.write("raiz")
        for estrategia in ("bfs", "dfs"):
            _, m = buscar(raiz, "alvo", estrategia)
            assert (m.pastas_abertas, m.itens_examinados, m.custo_g) == (1, 3, 3)
        print("OK: BFS/DFS, ordem, descoberta, custo, ausência, ciclos, validação e medições.")
    finally:
        for pasta, dirs, arquivos in os.walk(raiz, topdown=False):
            for nome in arquivos:
                os.unlink(os.path.join(pasta, nome))
            for nome in dirs:
                caminho = os.path.join(pasta, nome)
                if os.path.islink(caminho):
                    os.unlink(caminho)
                else:
                    os.rmdir(caminho)
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
