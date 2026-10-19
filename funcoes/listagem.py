"""Listagem determinística de diretórios, sem seguir links simbólicos."""

import os


def validar_caminho(caminho):
    """Retorne caminho absoluto sem apagar componentes antes de verificar links.

    Preservar '..' evita transformar 'link/../pasta' em um caminho aparentemente
    seguro antes de conferir o link. O sistema valida existência e tipo ao abrir.
    """
    absoluto = os.fsdecode(os.fspath(caminho))
    if not os.path.isabs(absoluto):
        absoluto = os.path.join(os.getcwd(), absoluto)
    componente = os.path.sep
    for parte in absoluto.split(os.path.sep):
        if not parte:
            continue
        componente = os.path.join(componente, parte)
        if os.path.islink(componente):
            raise ValueError("Links simbólicos não são permitidos: " + componente)
    return absoluto


def listar_dir(caminho):
    """Retorne arquivos regulares e pastas como DirEntry, ordenados por nome.

    Rejeita links também nos componentes do caminho. Erros do sistema de
    arquivos são propagados; o iterador scandir é sempre fechado.
    """
    absoluto = validar_caminho(caminho)
    with os.scandir(absoluto) as entradas:
        itens = [
            entrada for entrada in entradas
            if not entrada.is_symlink()
            and (entrada.is_dir(follow_symlinks=False)
                 or entrada.is_file(follow_symlinks=False))
        ]
    itens.sort(key=lambda entrada: entrada.name)
    return itens
