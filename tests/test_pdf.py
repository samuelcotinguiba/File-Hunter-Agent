"""PDFs reais, comprimidos, sem texto e protegidos; testes extras com pypdf."""

import os

from funcoes import pdf
from main import executar
from .pdf_exemplo import criar_pdf


def main():
    """Verifique leitura contada, extração interna e erros explícitos."""
    raiz = os.path.join(os.getcwd(), "tests", "pdf_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        caminho = os.path.join(raiz, "documento.pdf")
        criar_pdf(caminho, ["Inicio sem alvo", "Um ALGORITMO de busca", "Ultima pagina"])
        if pdf.PdfReader is None:
            try:
                pdf.ler_pdf(caminho, "algoritmo")
            except RuntimeError as erro:
                assert "requirements.txt" in str(erro)
            else:
                raise AssertionError("PDF aceito sem extrator")
            print("OK: ausência de pypdf sinalizada; extração PDF requer testes pelo Python da .venv.")
            return
        from pypdf import PdfReader, PdfWriter
        # O wrapper contabiliza releituras após seek, sem contar apenas filesize.
        with open(caminho, "rb") as arquivo:
            leitor = pdf._LeitorContado(arquivo)
            assert leitor.read(4) == b"%PDF"
            leitor.seek(0)
            assert len(leitor.readline()) == 9
            leitor.seek(0)
            assert leitor.readinto(bytearray(2)) == 2
            assert leitor.bytes_lidos == 15
        resultado, custo = pdf.ler_pdf(caminho, "algoritmo")
        assert resultado and custo > 0
        for algoritmo in ("bfs", "dfs", "ucs", "astar"):
            caminhos, m = executar(raiz, "algoritmo", algoritmo, "conteudo", alfa=0)
            assert caminhos == [caminho] and m.custo_g == custo and m.arquivos_lidos == 1
            assert m.pastas_abertas == 1
        leitor = PdfReader(caminho)
        escritor = PdfWriter()
        for pagina in leitor.pages:
            pagina = escritor.add_page(pagina)
            pagina.compress_content_streams()
        comprimido = os.path.join(raiz, "comprimido.PDF")
        with open(comprimido, "wb") as arquivo:
            escritor.write(arquivo)
        with open(comprimido, "rb") as arquivo:
            assert b"ALGORITMO" not in arquivo.read()
        assert pdf.ler_pdf(comprimido, "algoritmo")[0]
        fronteiras = os.path.join(raiz, "fronteiras.pdf")
        for paginas in (["fim"], ["inicio", "fim"], ["inicio", "", "fim"]):
            criar_pdf(fronteiras, paginas)
            # Oráculo: uma quebra ENTRE páginas, nenhuma quebra final artificial.
            texto = "\n".join(p.extract_text() or "" for p in PdfReader(fronteiras).pages).casefold()
            custos = set()
            for termo in ("fim", "fim\n", "inicio\nfim", "inicio\n\nfim", "ausente"):
                achou, bytes_lidos = pdf.ler_pdf(fronteiras, termo)
                assert achou == (termo in texto), (paginas, termo, texto)
                custos.add(bytes_lidos)
            assert len(custos) == 1  # Encontrar cedo não evita ler as outras páginas.
        vazio = os.path.join(raiz, "sem_texto.pdf")
        criar_pdf(vazio, [""])
        assert not pdf.ler_pdf(vazio, "algoritmo")[0]
        corrompido = os.path.join(raiz, "corrompido.pdf")
        with open(corrompido, "wb") as arquivo:
            arquivo.write(b"%PDF-1.4\n%%EOF\n")
        try:
            pdf.ler_pdf(corrompido, "algoritmo")
        except ValueError as erro:
            assert corrompido in str(erro)
        else:
            raise AssertionError("PDF corrompido aceito")
        protegido = os.path.join(raiz, "protegido.pdf")
        escritor = PdfWriter()
        escritor.add_page(leitor.pages[0])
        escritor.encrypt("senha")
        with open(protegido, "wb") as arquivo:
            escritor.write(arquivo)
        try:
            pdf.ler_pdf(protegido, "algoritmo")
        except ValueError as erro:
            assert protegido in str(erro)
        else:
            raise AssertionError("PDF protegido aceito")
        obter_original = pdf.PdfReader
        pdf.PdfReader = None
        try:
            nomes, m = executar(raiz, "documento.pdf", "bfs", "nome")
            assert nomes == [caminho] and m.arquivos_lidos == 0
            try:
                pdf.ler_pdf(caminho, "algoritmo")
            except RuntimeError:
                pass
            else:
                raise AssertionError("PDF aceito sem biblioteca")
        finally:
            pdf.PdfReader = obter_original
        print("OK: PDF multipágina/comprimido, fronteiras sem falso positivo, bytes contados,")
        print("quatro buscas, sem texto, senha e dependência opcional.")
    finally:
        for nome in os.listdir(raiz):
            os.unlink(os.path.join(raiz, nome))
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
