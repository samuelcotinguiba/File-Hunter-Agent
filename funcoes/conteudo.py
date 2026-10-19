"""Correspondências por nome ou conteúdo e custo local de uma expansão."""

import os


EXTENSOES_TEXTO = frozenset((".txt", ".md", ".py"))


def validar_busca(alvo, modo):
    """Valide parâmetros antes de abrir qualquer diretório."""
    if not alvo:
        raise ValueError("O alvo não pode ser vazio.")
    if modo not in ("nome", "conteudo"):
        raise ValueError("Modo deve ser nome ou conteudo.")


def examinar_arquivos(itens, termo, modo, metricas):
    """Retorne (correspondências, custo local), examinando a pasta inteira.

    Nome: custo len(itens), sem leitura. Conteúdo: leia .txt/.md/.py uma vez
    e some len(bytes), antes da decodificação UTF-8 com errors='ignore'.
    Extensões são uma convenção explícita da árvore didática, não detecção MIME.
    """
    encontrados = []
    custo = len(itens) if modo == "nome" else 0
    for item in itens:
        if not item.is_file(follow_symlinks=False):
            continue
        if modo == "nome":
            corresponde = termo in item.name.casefold()
        elif os.path.splitext(item.name)[1].casefold() in EXTENSOES_TEXTO:
            with open(item.path, "rb") as arquivo:
                dados = arquivo.read()
            custo += len(dados)
            metricas.arquivos_lidos += 1
            corresponde = termo in dados.decode("utf-8", errors="ignore").casefold()
        else:
            continue
        if corresponde:
            encontrados.append(item.path)
    return encontrados, custo
