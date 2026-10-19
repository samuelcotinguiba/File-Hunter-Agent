"""Regressões de caminhos, leitura em blocos e isolamento de medições."""

import os
import tracemalloc

from funcoes.conteudo import ler_texto, TAMANHO_BLOCO
from funcoes.listagem import listar_dir
from funcoes.metricas import medir_memoria, medir_tempo
from main import executar


def leitura_integral(caminho, termo):
    """Referência independente que reproduz a leitura anterior."""
    with open(caminho, "rb") as arquivo:
        dados = arquivo.read()
    return termo in dados.decode("utf-8", errors="ignore").casefold(), len(dados)


def main():
    """Valide fronteiras de bloco e compare memória com a versão integral."""
    raiz = os.path.join(os.getcwd(), "tests", "revisao_" + str(os.getpid()))
    os.mkdir(raiz)
    caminho = os.path.join(raiz, "texto.txt")
    try:
        casos = (
            (b"x" * (TAMANHO_BLOCO - 3) + "Straße\r\n".encode(), "STRASSE"),
            (b"x" * 8191 + "á".encode() + b"\xff\r\nfim", "Á\r\nFIM"),
            (b"x" * 10 + b"a" * (TAMANHO_BLOCO * 2) + b"z", "a" * (TAMANHO_BLOCO * 2)),
            (b"\xff" * (TAMANHO_BLOCO + 10), "alvo"),
            (b"a" * (TAMANHO_BLOCO - 1) + b"\r\n", "\r\n"),
            (b"", "a"),
            (b"ALVO" + b"x" * TAMANHO_BLOCO, "alvo"),
        )
        for dados, alvo in casos:
            with open(caminho, "wb") as arquivo:
                arquivo.write(dados)
            termo = alvo.casefold()
            assert ler_texto(caminho, termo) == leitura_integral(caminho, termo)
        # Entradas inválidas devem falhar com ValueError antes de acessar a raiz.
        inexistente = os.path.join(raiz, "inexistente")
        for estrategia in ("bfs", "dfs", "ucs", "astar"):
            for modo in ("nome", "conteudo"):
                for alfa in ((0, 1) if estrategia == "astar" else (1,)):
                    for alvo in (None, "", 0, 123, False, b"alvo", ["alvo"], {"alvo": 1}):
                        try:
                            executar(inexistente, alvo, estrategia, modo, alfa)
                        except ValueError as erro:
                            assert "alvo" in str(erro).lower()
                        else:
                            raise AssertionError("Alvo inválido aceito")
        os.symlink(raiz, os.path.join(raiz, "link"))
        for entrada in (os.path.join(raiz, "link"),
                        os.path.join(raiz, "link", "..", os.path.basename(raiz))):
            for estrategia in ("bfs", "dfs", "ucs"):
                try:
                    executar(entrada, "texto", estrategia)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Symlink oculto por '..' foi aceito")
            try:
                listar_dir(entrada)
            except ValueError:
                pass
            else:
                raise AssertionError("listagem seguiu symlink")
        try:
            listar_dir(os.path.join(raiz, "inexistente", ".."))
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("Componente inexistente foi normalizado")
        with open(caminho, "wb") as arquivo:
            for _ in range(64):
                arquivo.write(b"x" * TAMANHO_BLOCO)
            arquivo.write(b"alvo")
        referencia, pico_integral = medir_memoria(leitura_integral, caminho, "alvo")
        resultado, pico_blocos = medir_memoria(ler_texto, caminho, "alvo")
        assert resultado == referencia == (True, 4 * 1024 * 1024 + 4)
        assert pico_blocos < pico_integral / 4
        tracemalloc.start()
        try:
            for medir in (medir_memoria, medir_tempo):
                try:
                    medir(lambda: None)
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("Medição aceitou tracing já ativo")
                assert tracemalloc.is_tracing()
        finally:
            tracemalloc.stop()
        def falhar():
            raise ValueError("Falha simulada")
        try:
            medir_memoria(falhar)
        except ValueError:
            assert not tracemalloc.is_tracing()
        else:
            raise AssertionError("Exceção não propagada")
        print("OK: termos entre blocos, Unicode, CRLF, bytes inválidos, caminhos e medições.")
        print("OK: alvos vazios ou de tipo inválido geram ValueError nas quatro buscas, antes de acessar a raiz.")
        print(f"Arquivo de 4 MiB: pico integral {pico_integral:.1f} KiB; "
              f"em blocos {pico_blocos:.1f} KiB.")
    finally:
        if os.path.islink(os.path.join(raiz, "link")):
            os.unlink(os.path.join(raiz, "link"))
        if os.path.exists(caminho):
            os.unlink(caminho)
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
