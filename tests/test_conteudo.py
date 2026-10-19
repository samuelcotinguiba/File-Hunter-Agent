"""Verifique custo em bytes reais, UTF-8 e exclusão de binários."""

import os

from main import executar


def main():
    """Confira caminhos baratos e caros sem depender do leitor da busca."""
    raiz = os.path.join(os.getcwd(), "tests", "conteudo_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        os.mkdir(os.path.join(raiz, "a_cara"))
        os.makedirs(os.path.join(raiz, "z_barata", "profunda"))
        os.mkdir(os.path.join(raiz, "vazia"))
        dados = {
            "origem.py": "á\r\n".encode("utf-8"),
            "imagem.png": b"algoritmo" * 100,
            "binario.bin": b"algoritmo",
            "a_cara/neutro.txt": b"ALGORITMO" + b"x" * 100,
            "z_barata/profunda/a.MD": b"\xffAlGoRiTmO\r\n",
            "z_barata/profunda/z.txt": b"x" * 10,
        }
        for nome, conteudo in dados.items():
            with open(os.path.join(raiz, nome), "wb") as arquivo:
                arquivo.write(conteudo)
        os.symlink(raiz, os.path.join(raiz, "z_barata", "ciclo"))
        os.symlink(os.path.join(raiz, "imagem.png"), os.path.join(raiz, "atalho.txt"))
        custo_raiz = len(dados["origem.py"])
        caro = custo_raiz + len(dados["a_cara/neutro.txt"])
        barato = custo_raiz + len(dados["z_barata/profunda/a.MD"]) + 10
        assert (caro, barato) == (113, 26)
        for estrategia in ("bfs", "dfs", "ucs"):
            caminhos, m = executar(raiz, "Algoritmo", estrategia, "conteudo")
            esperado = ("z_barata/profunda/a.MD" if estrategia == "ucs"
                        else "a_cara/neutro.txt")
            assert caminhos == [os.path.join(raiz, esperado)]
            assert m.custo_g == (barato if estrategia == "ucs" else caro)
            assert m.arquivos_lidos == (4 if estrategia == "ucs" else 2)
            caminhos, m = executar(raiz, "ausente", estrategia, "conteudo")
            assert caminhos == [] and m.custo_g == 0
            assert m.arquivos_lidos == 4 and m.pastas_abertas == 5
            caminhos, m = executar(raiz, "Á", estrategia, "conteudo")
            assert caminhos == [os.path.join(raiz, "origem.py")]
            assert m.custo_g == 4 and m.arquivos_lidos == 1
            caminhos, m = executar(raiz, "imagem", estrategia, "nome")
            assert caminhos == [os.path.join(raiz, "imagem.png")]
            assert m.arquivos_lidos == 0 and m.custo_g == 6
            try:
                executar(raiz, "alvo", estrategia, "invalido")
            except ValueError:
                pass
            else:
                raise AssertionError("Modo inválido aceito")
        # Arquivos vazios contam como lidos e não acrescentam bytes ao custo.
        for nome in ("a_cara/vazio.md", "a_cara/outro.py"):
            with open(os.path.join(raiz, nome), "wb") as arquivo:
                arquivo.write(b"")
        _, m = executar(raiz, "ausente", "ucs", "conteudo")
        assert m.arquivos_lidos == 6 and m.custo_g == 0
        with open(os.path.join(raiz, "z_barata/profunda/z.txt"), "wb") as arquivo:
            arquivo.write(b"algoritmo!")
        caminhos, m = executar(raiz, "algoritmo", "ucs", "conteudo")
        assert len(caminhos) == 2 and m.custo_g == barato
        print("OK: conteúdo em BFS/DFS/UCS; UCS 26 bytes contra 113; UTF-8 inválido,")
        print("acentos, CRLF, binários, arquivos vazios, ciclos e leitura integral da pasta.")
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
