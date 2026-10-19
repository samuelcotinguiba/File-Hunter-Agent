"""Valide UCS contra um oráculo de custos de todos os objetivos da árvore."""

import os

from funcoes.bfs_dfs import bfs
from funcoes.listagem import listar_dir
from funcoes.ucs import ucs
from main import executar


def objetivos(raiz, termo):
    """Enumere custos exatos sem heap para conferir o mínimo independentemente."""
    custos = {}
    pendentes = [(raiz, 0)]
    while pendentes:
        pasta, pai = pendentes.pop()
        itens = listar_dir(pasta)
        custo = pai + len(itens)
        for item in itens:
            if item.is_dir(follow_symlinks=False):
                pendentes.append((item.path, custo))
            elif termo.casefold() in item.name.casefold():
                custos[item.path] = custo
    return custos


def main():
    """Teste alvo caro descoberto primeiro, empates, ciclos e ausência."""
    raiz = os.path.join(os.getcwd(), "tests", "ucs_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        os.mkdir(os.path.join(raiz, "a_cara"))
        os.makedirs(os.path.join(raiz, "z_barata", "profunda"))
        nomes = ["a_cara/ALVO.txt", "z_barata/profunda/alvo.md"]
        nomes += ["a_cara/extra_" + str(i) + ".txt" for i in range(10)]
        for nome in nomes:
            with open(os.path.join(raiz, nome), "w") as arquivo:
                arquivo.write("teste")
        os.symlink(raiz, os.path.join(raiz, "z_barata", "ciclo"))
        caminhos_bfs, m_bfs = bfs(raiz, "alvo")
        caminhos, m = ucs(raiz, "AlVo")
        assert caminhos_bfs == [os.path.join(raiz, "a_cara", "ALVO.txt")]
        assert caminhos == [os.path.join(raiz, "z_barata", "profunda", "alvo.md")]
        assert m_bfs.custo_g == 13 and m.custo_g == 4
        assert (m.pastas_abertas, m.itens_examinados) == (4, 15)
        assert m.arquivos_encontrados == 2 and m.arquivos_lidos == 0
        for termo in ("alvo", ".txt", "extra_1", "ausente", ".md"):
            custos = objetivos(raiz, termo)
            caminhos, m = executar(raiz, termo, "ucs")
            if custos:
                assert m.custo_g == min(custos.values())
                assert all(custos[p] == m.custo_g for p in caminhos)
            else:
                assert caminhos == [] and m.custo_g == 0
                assert m.pastas_abertas == 4
        for pasta in ("b_empate", "c_empate"):
            os.mkdir(os.path.join(raiz, pasta))
            with open(os.path.join(raiz, pasta, "igual.txt"), "w") as arquivo:
                arquivo.write("empate")
        caminhos, m = ucs(raiz, "igual")
        assert caminhos == [os.path.join(raiz, "b_empate", "igual.txt")]
        assert m.custo_g == 5
        with open(os.path.join(raiz, "alvo.txt"), "w") as arquivo:
            arquivo.write("raiz")
        caminhos, m = ucs(raiz, "alvo")
        assert caminhos == [os.path.join(raiz, "alvo.txt")]
        assert m.custo_g == 5 and m.pastas_abertas == 1
        try:
            ucs(raiz, "")
        except ValueError:
            pass
        else:
            raise AssertionError("Alvo vazio aceito")
        print("OK: UCS escolheu custo 4 contra BFS 13; oráculo, empates, ciclos e medições.")
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
