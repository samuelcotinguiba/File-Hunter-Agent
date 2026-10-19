"""Seleção de pastas, navegação no terminal e preferência local em JSON."""

import json
import os
import subprocess
import time

from .listagem import listar_dir, validar_caminho


RAIZ_PADRAO = "./docencia/fontes"
ARQUIVO_CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              ".file_hunter.json")

# O caminho é passado por argv, sem interpolação em código AppleScript ou shell.
_DIALOGO_MACOS = '''on run argv
    try
        set inicial to POSIX file (item 1 of argv) as alias
        set escolhida to choose folder with prompt "File Hunter Agent — escolha a pasta" default location inicial
        return POSIX path of escolhida
    on error number -128
        return ""
    end try
end run'''


def validar_pasta(caminho):
    """Valide a pasta sem listar seu conteúdo nem ocultar componentes symlink."""
    absoluto = validar_caminho(os.path.expanduser(os.fspath(caminho)))
    if not os.path.isdir(absoluto):
        raise ValueError(f"Pasta inexistente ou indisponível: {absoluto}")
    return os.path.normpath(absoluto)


def _validar_config(config):
    """Exija destino JSON e rejeite componentes simbólicos do caminho."""
    config = validar_caminho(config)
    if not config.casefold().endswith(".json"):
        raise ValueError("O arquivo de preferências deve ter extensão .json.")
    return config


def carregar_ultimo_caminho(config=ARQUIVO_CONFIG):
    """Leia a preferência; arquivo ausente retorna None e conteúdo inválido falha."""
    config = _validar_config(config)
    try:
        with open(config, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        return None
    if (not isinstance(dados, dict) or type(dados.get("versao")) is not int
            or dados["versao"] != 1 or not isinstance(dados.get("ultimo_caminho"), str)
            or not os.path.isabs(dados["ultimo_caminho"])):
        raise ValueError("Preferências devem conter versao=1 e ultimo_caminho absoluto.")
    return validar_pasta(dados["ultimo_caminho"])


def salvar_ultimo_caminho(pasta, config=ARQUIVO_CONFIG):
    """Substitua o JSON somente após concluir a escrita de um temporário exclusivo."""
    pasta = validar_pasta(pasta)
    config = _validar_config(config)
    os.makedirs(os.path.dirname(config), exist_ok=True)
    temporario = f"{config}.{os.getpid()}.{time.time_ns()}.tmp"
    arquivo = open(temporario, "x", encoding="utf-8")
    try:
        with arquivo:
            json.dump({"versao": 1, "ultimo_caminho": pasta}, arquivo,
                      ensure_ascii=False, indent=2, allow_nan=False)
            arquivo.write("\n")
        os.replace(temporario, config)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)
    return pasta


def lembrar_pasta(pasta, config=ARQUIVO_CONFIG):
    """Uma falha na preferência é informada e não impede executar uma busca."""
    pasta = validar_pasta(pasta)
    try:
        salvar_ultimo_caminho(pasta, config)
    except (OSError, ValueError) as erro:
        print(f"Aviso: não foi possível salvar a última pasta: {erro}")
    return pasta


def raiz_inicial(raiz=None, config=ARQUIVO_CONFIG, usar_ultima=True):
    """Priorize --raiz; restaure preferência somente nos fluxos interativos."""
    if raiz is not None:
        return raiz
    if usar_ultima:
        try:
            anterior = carregar_ultimo_caminho(config)
        except (OSError, ValueError) as erro:
            print(f"Aviso: última pasta não restaurada: {erro}")
        else:
            if anterior is not None:
                return anterior
    return RAIZ_PADRAO


def _inicio_navegacao(inicial):
    """Use o diretório de trabalho quando a pasta inicial não existir."""
    inicial = validar_caminho(os.path.expanduser(os.fspath(inicial)))
    if not os.path.isdir(inicial):
        print("Pasta inicial indisponível; navegação iniciada no diretório de trabalho.")
        inicial = os.getcwd()
    return validar_pasta(inicial)


def _dialogo_tk(inicial):
    """Abra o diálogo nativo de diretórios; Tk é importado apenas quando usado."""
    try:
        import tkinter
        from tkinter import filedialog
    except ImportError as erro:
        raise RuntimeError("Tkinter não está disponível neste Python.") from erro
    janela = None
    try:
        janela = tkinter.Tk()
        janela.withdraw()
        return filedialog.askdirectory(parent=janela, title="File Hunter Agent — escolha a pasta",
                                       initialdir=inicial, mustexist=True)
    except tkinter.TclError as erro:
        raise RuntimeError(f"Não foi possível abrir o seletor gráfico: {erro}") from erro
    finally:
        if janela is not None:
            try:
                janela.destroy()
            except tkinter.TclError:
                pass  # O diálogo pode ter encerrado a janela durante uma falha.


def abrir_seletor(inicial):
    """Use o seletor do macOS ou o diálogo nativo via Tk nas demais plataformas."""
    inicial = _inicio_navegacao(inicial)
    if os.name == "posix" and os.uname().sysname == "Darwin":
        try:
            resposta = subprocess.run(["/usr/bin/osascript", "-e", _DIALOGO_MACOS, inicial],
                                      capture_output=True, text=True, check=True)
        except (OSError, subprocess.CalledProcessError) as erro:
            raise RuntimeError("O seletor de pastas do macOS está indisponível.") from erro
        caminho = resposta.stdout.strip()
    else:
        caminho = _dialogo_tk(inicial)
    return validar_pasta(caminho) if caminho else None


def navegar_terminal(inicial):
    """Retorne (pasta, sugestão de nome) ou None; nunca abra conteúdos de arquivos."""
    atual = _inicio_navegacao(inicial)
    while True:
        try:
            itens = listar_dir(atual)
        except OSError as erro:
            print(f"Não foi possível listar a pasta: {erro}")
            return None
        print(f"\nPasta: {atual}")
        for indice, item in enumerate(itens, 1):
            tipo = "pasta" if item.is_dir(follow_symlinks=False) else "arquivo"
            print(f"{indice}. [{tipo}] {item.name!r}")
        print("u. Usar esta pasta | .. Subir | p. Digitar caminho | 0. Cancelar")
        opcao = input("Pasta ou arquivo: ").strip()
        if opcao == "0":
            return None
        if opcao.lower() == "u":
            return atual, None
        if opcao == "..":
            atual = os.path.dirname(atual)
            continue
        try:
            if opcao.lower() == "p":
                atual = validar_pasta(input("Caminho da pasta: ").strip())
            elif opcao.isdecimal() and 1 <= int(opcao) <= len(itens):
                item = itens[int(opcao) - 1]
                if item.is_dir(follow_symlinks=False):
                    atual = validar_pasta(item.path)
                else:
                    validar_caminho(item.path)
                    if not os.path.isfile(item.path):
                        raise ValueError("O arquivo não está mais disponível.")
                    print(f"Nome sugerido para busca: {item.name} (correspondência parcial).")
                    return atual, item.name
            else:
                print("Opção inválida; escolha um número ou um dos comandos exibidos.")
        except (OSError, ValueError) as erro:
            print(f"Não foi possível selecionar: {erro}")


def selecionar_pasta(inicial):
    """Se o seletor nativo estiver indisponível, ofereça a navegação no terminal."""
    try:
        escolhida = abrir_seletor(inicial)
    except RuntimeError as erro:
        print(f"{erro} Usando navegação pelo terminal.")
        return navegar_terminal(inicial)
    return (escolhida, None) if escolhida is not None else None


def menu_pastas(inicial):
    """Submenu de seleção inspirado no gerenciamento do projeto Binary-Search-Tree."""
    while True:
        print("\n1. Seletor do sistema\n2. Navegar no terminal\n3. Digitar caminho\n0. Voltar")
        opcao = input("Escolher pasta: ").strip()
        try:
            if opcao == "0":
                return None
            if opcao == "1":
                return selecionar_pasta(inicial)
            if opcao == "2":
                return navegar_terminal(inicial)
            if opcao == "3":
                return validar_pasta(input("Caminho da pasta: ").strip()), None
            print("Opção inválida; escolha de 0 a 3.")
        except (OSError, ValueError) as erro:
            print(f"Não foi possível selecionar a pasta: {erro}")
