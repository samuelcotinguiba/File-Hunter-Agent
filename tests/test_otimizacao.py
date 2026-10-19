"""Objetivos confirmados não exigem preparar seus descendentes no heap."""

import os

from funcoes.astar import astar
from funcoes.ucs import ucs


def main():
    """Confira economia de consultas e preservação do menor custo e desempates."""
    raiz = os.path.join(os.getcwd(), "tests", "otimizacao_" + str(os.getpid()))
    larga = os.path.join(raiz, "larga")
    os.makedirs(larga)
    try:
        for i in range(64):
            os.mkdir(os.path.join(larga, f"pasta_{i:03d}"))
        with open(os.path.join(larga, "alvo.txt"), "w") as arquivo:
            arquivo.write("algoritmo")
        realpath_original = os.path.realpath
        consultas = []

        def contar(caminho, *args, **kwargs):
            consultas.append(caminho)
            return realpath_original(caminho, *args, **kwargs)

        for funcao, opcoes in ((ucs, {}), (astar, {"alfa": 0}), (astar, {"alfa": 1000})):
            for modo, termo in (("nome", "alvo"), ("conteudo", "algoritmo")):
                consultas.clear()
                visitas = []
                os.path.realpath = contar
                try:
                    caminhos, m = funcao(larga, termo, modo, visitas=visitas, **opcoes)
                finally:
                    os.path.realpath = realpath_original
                assert caminhos == [os.path.join(larga, "alvo.txt")]
                assert m.pastas_abertas == 1 and m.itens_examinados == 65
                assert m.arquivos_encontrados == 1
                assert m.custo_g == (65 if modo == "nome" else 9)
                assert m.arquivos_lidos == int(modo == "conteudo")
                assert consultas == [larga]  # Nenhuma consulta aos 64 descendentes.
                assert visitas == [{"diretorio": larga, "custo_local": m.custo_g, "g": m.custo_g}]

        selecao = os.path.join(raiz, "selecao")
        cara = os.path.join(selecao, "a_cara")
        barata = os.path.join(selecao, "z_barata")
        os.makedirs(os.path.join(cara, "filha"))
        os.mkdir(barata)
        for pasta, texto in ((cara, "algoritmo" + "x" * 200),
                             (os.path.join(cara, "filha"), "algoritmo"), (barata, "algoritmo")):
            with open(os.path.join(pasta, "alvo.txt"), "w") as arquivo:
                arquivo.write(texto)
        for i in range(8):
            with open(os.path.join(cara, f"extra_{i}.txt"), "w") as arquivo:
                arquivo.write("x" * 16)
        for modo, termo, custo in (("nome", "alvo", 3), ("conteudo", "algoritmo", 9)):
            visitas = []
            caminhos, m = ucs(selecao, termo, modo, visitas=visitas)
            assert caminhos == [os.path.join(barata, "alvo.txt")] and m.custo_g == custo
            assert m.pastas_abertas == 3 and m.arquivos_encontrados == 2
            assert [v["diretorio"] for v in visitas] == [selecao, cara, barata]
            assert astar(selecao, termo, modo, alfa=0) == (caminhos, m)
        for funcao in (ucs, astar):
            caminhos, m = funcao(larga, "ausente")
            assert caminhos == [] and m.pastas_abertas == 65  # Ausência continua exaustiva.
        print("OK: UCS/A* consultam só a raiz objetivo, sem preparar 64 descendentes;")
        print("custos 3 itens/9 bytes, candidatos concorrentes, alfa zero e ausência preservados.")
    finally:
        for pasta, dirs, arquivos in os.walk(raiz, topdown=False):
            for nome in arquivos:
                os.unlink(os.path.join(pasta, nome))
            for nome in dirs:
                os.rmdir(os.path.join(pasta, nome))
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
