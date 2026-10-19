"""Jaccard de bigramas e heurística não admissível baseada no nome da pasta."""

import os


def bigramas(texto):
    """Retorne pares de caracteres após casefold; texto unitário é um token."""
    texto = texto.casefold()
    if len(texto) < 2:
        return {texto} if texto else set()
    return {texto[i:i + 2] for i in range(len(texto) - 1)}


def _jaccard(a, b):
    """Compare conjuntos sem alocar a união."""
    intersecao = len(a & b)
    uniao = len(a) + len(b) - intersecao
    return intersecao / uniao if uniao else 1.0


def similaridade(nome_pasta, termo):
    """Jaccard em [0, 1]; dois textos vazios têm similaridade 1."""
    return _jaccard(bigramas(nome_pasta), bigramas(termo))


def validar_alfa(alfa):
    """Aceite apenas peso finito e não negativo, sem dependências adicionais."""
    alfa = float(alfa)
    if not 0 <= alfa < float("inf"):
        raise ValueError("alfa deve ser finito e não negativo.")
    return alfa


def heuristica(nome_pasta, termo, alfa=1.0):
    """Calcule alfa*(1-similaridade); não garante admissibilidade ou ótimo."""
    return validar_alfa(alfa) * (1 - similaridade(nome_pasta, termo))


def criar_estimador(termo, alfa):
    """Prepare o termo uma vez por busca e estime somente pelo nome da pasta."""
    alfa = validar_alfa(alfa)
    referencia = bigramas(termo)

    def estimar(caminho):
        nome = os.path.basename(os.path.normpath(caminho))
        return alfa * (1 - _jaccard(bigramas(nome), referencia))

    return estimar
