"""Correspondências por nome ou conteúdo e custo local de uma expansão."""

import os

from .pdf import ler_pdf


EXTENSOES_TEXTO = frozenset((
    ".txt", ".md", ".rst", ".py", ".csv", ".tsv", ".json", ".jsonl", ".log",
    ".xml", ".html", ".htm", ".svg", ".css", ".js", ".ts", ".yaml", ".yml",
    ".ini", ".cfg", ".toml", ".sql", ".tex", ".sh", ".c", ".cpp", ".h",
    ".java", ".go", ".rs",
))
TAMANHO_BLOCO = 64 * 1024


def ler_texto(caminho, termo):
    """Retorne (contém termo casefold, bytes consumidos) com memória limitada.

    TextIOWrapper preserva UTF-8 entre blocos e ignora sequências inválidas.
    A sobreposição após casefold conserva termos que atravessam os blocos.
    newline='' preserva CRLF. Após EOF, buffer.tell() informa o deslocamento
    binário real desde o início, incluindo os bytes descartados na decodificação.
    """
    corresponde = False
    cauda = ""
    sobreposicao = len(termo) - 1
    with open(caminho, encoding="utf-8", errors="ignore", newline="") as arquivo:
        while True:
            bloco = arquivo.read(TAMANHO_BLOCO)
            if not bloco:
                break
            if not corresponde:
                texto = cauda + bloco.casefold()
                corresponde = termo in texto
                if corresponde:
                    # Não retenha a janela (possivelmente longa) até EOF.
                    cauda = ""
                    del texto
                else:
                    cauda = texto[-sobreposicao:] if sobreposicao else ""
        return corresponde, arquivo.buffer.tell()


def validar_busca(alvo, modo):
    """Valide parâmetros antes de abrir qualquer diretório."""
    if not alvo:
        raise ValueError("O alvo não pode ser vazio.")
    if modo not in ("nome", "conteudo"):
        raise ValueError("Modo deve ser nome ou conteudo.")


def examinar_arquivos(itens, termo, modo, metricas):
    """Retorne (correspondências, custo local), examinando a pasta inteira.

    Nome: qualquer extensão, custo len(itens), sem leitura. Conteúdo: leia
    somente as extensões de texto declaradas em EXTENSOES_TEXTO uma vez,
    em blocos e some bytes reais, incluindo os ignorados ao decodificar.
    Extensões são uma convenção explícita da árvore didática, não detecção MIME.
    """
    encontrados = []
    custo = len(itens) if modo == "nome" else 0
    for item in itens:
        if not item.is_file(follow_symlinks=False):
            continue
        if modo == "nome":
            corresponde = termo in item.name.casefold()
        else:
            extensao = os.path.splitext(item.name)[1].casefold()
            if extensao in EXTENSOES_TEXTO:
                corresponde, bytes_lidos = ler_texto(item.path, termo)
            elif extensao == ".pdf":
                corresponde, bytes_lidos = ler_pdf(item.path, termo)
            else:
                continue
            custo += bytes_lidos
            metricas.arquivos_lidos += 1
        if corresponde:
            encontrados.append(item.path)
    return encontrados, custo
