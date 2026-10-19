"""Regressões para subpastas, nomes de qualquer formato e textos adicionais."""

import os

from funcoes.conteudo import EXTENSOES_TEXTO
from main import executar


def main():
    """Percorra quatro níveis sem ler PDF/Office/binários como texto."""
    raiz = os.path.join(os.getcwd(), "tests", "formatos_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        profunda = os.path.join(raiz, "nivel1", "nivel2", "nivel3", "nivel4")
        os.makedirs(profunda)
        # As fixtures binárias verificam localização pelo nome, não interpretação.
        nomes_binarios = ("Livro.PDF", "aula.docx", "notas.xlsx", "slides.pptx",
                          "pacote.zip", "imagem.png", "programa.exe", "SEM_EXTENSAO")
        for nome in nomes_binarios:
            with open(os.path.join(profunda, nome), "wb") as arquivo:
                arquivo.write(b"\x00algoritmo\xff")
        textos = {"tabela.CSV": "nome,assunto\nA,algoritmo\n",
                  "config.JSON": '{"tema": "ALGORITMO"}\n',
                  "evento.log": "Iniciando algoritmo\n",
                  "pagina.html": "<p>Algoritmo</p>\n"}
        for nome, dados in textos.items():
            with open(os.path.join(profunda, nome), "w", encoding="utf-8", newline="") as arquivo:
                arquivo.write(dados)
        os.symlink(raiz, os.path.join(profunda, "ciclo"))
        for algoritmo in ("bfs", "dfs", "ucs", "astar"):
            caminhos, _ = executar(raiz, ".pdf", algoritmo, "nome", alfa=0)
            assert caminhos == [os.path.join(profunda, "Livro.PDF")]
            for nome in nomes_binarios:
                caminhos, m = executar(raiz, nome.lower(), algoritmo, "nome", alfa=0)
                assert caminhos == [os.path.join(profunda, nome)]
                assert m.pastas_abertas == 5 and m.arquivos_lidos == 0
                assert m.itens_examinados == 16 and m.custo_g == 16
            caminhos, m = executar(raiz, "algoritmo", algoritmo, "conteudo", alfa=0)
            assert set(caminhos) == {os.path.join(profunda, nome) for nome in textos}
            assert m.arquivos_lidos == 4 and m.arquivos_encontrados == 4
            assert m.custo_g == sum(len(dados.encode("utf-8")) for dados in textos.values())
            assert m.pastas_abertas == 5 and m.itens_examinados == 16
            caminhos, m = executar(raiz, ".pdf", algoritmo, "conteudo", alfa=0)
            assert caminhos == [] and m.custo_g == 0 and m.arquivos_lidos == 4
        assert not EXTENSOES_TEXTO.intersection({".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".exe"})
        print("OK: quatro níveis; PDF, Office, ZIP, imagens e sem extensão por nome nos quatro algoritmos.")
        print("CSV/JSON/LOG/HTML por conteúdo; binários não lidos; custos e ciclos preservados.")
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
