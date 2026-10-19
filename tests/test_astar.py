"""Regressões da heurística, A* e equivalência com UCS para alfa zero."""

import os

from funcoes.astar import astar
from funcoes.heuristica import bigramas, heuristica, similaridade
from funcoes.ucs import ucs
from main import executar


def main():
    """Demonstre orientação heurística e contraexemplo de otimalidade."""
    assert similaridade("ABC", "abd") == 1 / 3
    assert similaridade("", "") == 1 and similaridade("", "a") == 0
    assert similaridade("a", "A") == 1 and similaridade("a", "b") == 0
    assert similaridade("Straße", "STRASSE") == 1
    assert bigramas("aaaa") == {"aa"}
    assert heuristica("algoritmo", "ALGORITMO", 1000) == 0
    assert heuristica("zz", "algoritmo", 1000) == 1000
    raiz = os.path.join(os.getcwd(), "tests", "astar_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        for pasta in ("algoritmo", "zz"):
            os.mkdir(os.path.join(raiz, pasta))
        for nome, dados in (("algoritmo/algoritmo.txt", b"algoritmo" + b"x" * 100),
                            ("zz/algoritmo.md", b"algoritmo")):
            with open(os.path.join(raiz, nome), "wb") as arquivo:
                arquivo.write(dados)
        for indice in range(10):
            with open(os.path.join(raiz, "algoritmo", f"extra_{indice}.txt"), "w") as arquivo:
                arquivo.write("x")
        os.symlink(raiz, os.path.join(raiz, "algoritmo", "ciclo"))
        for modo, barato, caro in (("nome", 3, 13), ("conteudo", 9, 119)):
            caminhos_ucs, m_ucs = ucs(raiz, "algoritmo", modo)
            caminhos, m = executar(raiz, "algoritmo", "astar", modo, alfa=1000)
            assert caminhos_ucs == [os.path.join(raiz, "zz", "algoritmo.md")]
            assert caminhos == [os.path.join(raiz, "algoritmo", "algoritmo.txt")]
            assert (m_ucs.custo_g, m.custo_g) == (barato, caro)
            assert (m_ucs.pastas_abertas, m.pastas_abertas) == (3, 2)
            assert m.arquivos_lidos == (11 if modo == "conteudo" else 0)
            for termo in ("algoritmo", "ausente", "extra", "x"):
                assert astar(raiz, termo, modo, alfa=0) == ucs(raiz, termo, modo)
            caminhos, m = astar(raiz, "ausente", modo)
            assert caminhos == [] and m.custo_g == 0 and m.pastas_abertas == 3
        for alfa in (-1, float("nan"), float("inf"), -float("inf")):
            try:
                astar(raiz, "algoritmo", alfa=alfa)
            except ValueError:
                pass
            else:
                raise AssertionError("Peso inválido aceito")
        for caminho in (os.path.join(raiz, "algoritmo", "ciclo"),
                        os.path.join(raiz, "algoritmo", "ciclo", "..")):
            try:
                astar(caminho, "algoritmo")
            except ValueError:
                pass
            else:
                raise AssertionError("Raiz com symlink aceita")
        print("OK: Jaccard, alfa inválido, ciclos, ausência e A*(alfa=0) idêntico a UCS.")
        print("Contraexemplo: A* abriu 2 pastas, UCS 3; custos nome 13 vs 3, conteúdo 119 vs 9.")
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
