"""Execute todas as verificações com python3 -m tests."""

from .test_buscas import main as testar_buscas
from .test_ucs import main as testar_ucs
from .test_conteudo import main as testar_conteudo
from .test_revisao import main as testar_revisao
from .test_astar import main as testar_astar
from .test_relatorio import main as testar_relatorio
from .test_formatos import main as testar_formatos
from .test_pdf import main as testar_pdf
from .test_comparacao import main as testar_comparacao


def main():
    """Interrompa na primeira falha e informe sucesso somente ao finalizar."""
    for testar in (testar_buscas, testar_ucs, testar_conteudo, testar_revisao,
                   testar_astar, testar_relatorio, testar_formatos, testar_pdf,
                   testar_comparacao):
        testar()
    print("Todas as verificações passaram.")


if __name__ == "__main__":
    main()
