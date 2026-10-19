"""Extração opcional de PDF, isolada das políticas de busca e da interface."""

try:
    from pypdf import PdfReader, __version__
    from pypdf.errors import PyPdfError
except ImportError:
    PdfReader = None
    __version__ = None
    PyPdfError = ValueError


EXTRATOR_PDF = f"pypdf/{__version__}" if PdfReader is not None else "indisponível"


class _LeitorContado:
    """Conte bytes entregues ao parser, inclusive releituras após seek.

    O arquivo real continua aberto/fechado pelo chamador. read/readline/readinto
    são interceptados; demais operações seguem para o mesmo arquivo binário.
    """

    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.bytes_lidos = 0

    def read(self, tamanho=-1):
        dados = self.arquivo.read(tamanho)
        self.bytes_lidos += len(dados)
        return dados

    def readline(self, tamanho=-1):
        dados = self.arquivo.readline(tamanho)
        self.bytes_lidos += len(dados)
        return dados

    def readinto(self, buffer):
        quantidade = self.arquivo.readinto(buffer)
        self.bytes_lidos += quantidade or 0
        return quantidade

    def __getattr__(self, nome):
        return getattr(self.arquivo, nome)


def ler_pdf(caminho, termo):
    """Retorne (contém termo casefold, bytes lidos) de todas as páginas.

    Não faz OCR nem lê PDFs protegidos por senha. A extração é por página;
    o parser mantém suas próprias estruturas, sem a memória limitada dos TXT.
    Una os textos com uma quebra entre páginas, sem acrescentar quebra final.
    """
    if PdfReader is None:
        raise RuntimeError("Busca interna em PDF requer pypdf: instale requirements.txt "
                           "no ambiente virtual e execute com seu Python.")
    try:
        with open(caminho, "rb") as arquivo:
            contado = _LeitorContado(arquivo)
            leitor = PdfReader(contado)
            if leitor.is_encrypted:
                raise ValueError("PDF protegido por senha não é suportado")
            corresponde = False
            cauda = ""
            sobreposicao = len(termo) - 1
            for indice, pagina in enumerate(leitor.pages):
                texto = pagina.extract_text() or ""
                if not corresponde:
                    janela = cauda + ("\n" if indice else "") + texto.casefold()
                    corresponde = termo in janela
                    cauda = janela[-sobreposicao:] if sobreposicao and not corresponde else ""
                    del janela
            return corresponde, contado.bytes_lidos
    except (PyPdfError, ValueError, TypeError, NotImplementedError) as erro:
        raise ValueError(f"Não foi possível extrair texto do PDF {caminho}: {erro}") from erro
