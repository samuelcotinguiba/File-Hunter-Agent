"""Listagem determinística de diretórios, sem seguir links simbólicos."""

import os


def listar_dir(caminho):
    """Retorne arquivos regulares e pastas como DirEntry, ordenados por nome.

    Rejeita links também nos componentes do caminho. Erros do sistema de
    arquivos são propagados; o iterador scandir é sempre fechado.
    """
    absoluto = os.path.abspath(caminho)
    componente = absoluto
    while True:
        if os.path.islink(componente):
            raise ValueError("Links simbólicos não são permitidos: " + componente)
        pai = os.path.dirname(componente)
        if pai == componente:
            break
        componente = pai
    with os.scandir(absoluto) as entradas:
        itens = [
            entrada for entrada in entradas
            if not entrada.is_symlink()
            and (entrada.is_dir(follow_symlinks=False)
                 or entrada.is_file(follow_symlinks=False))
        ]
    return sorted(itens, key=lambda entrada: entrada.name)
