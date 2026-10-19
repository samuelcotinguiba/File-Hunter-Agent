"""A* por nome ou conteúdo, sem garantia de caminho ótimo."""

from .heuristica import criar_estimador, validar_alfa
from .ucs import _buscar_prioridade


def astar(raiz, alvo, modo="nome", alfa=1.0):
    """Oriente o heap por g+h com similaridade do nome da pasta ao alvo.

    A heurística não é admissível. Pastas pendentes usam g do pai, pois o custo
    da própria pasta exige expansão. Candidaturas confirmadas usam g exato e h=0.
    alfa=0 reproduz UCS, inclusive os desempates e as contagens.
    """
    alfa = validar_alfa(alfa)
    estimar = criar_estimador(alvo, alfa) if alfa else None
    return _buscar_prioridade(raiz, alvo, modo, estimar)
