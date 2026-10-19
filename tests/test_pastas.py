"""Preferências, seleção nativa simulada e navegação sem leitura de conteúdos."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import main as interface
from funcoes import pastas
from funcoes.metricas import Metricas


def main():
    """Verifique a interface isoladamente, sem abrir janelas durante os testes."""
    raiz = os.path.join(os.getcwd(), "tests", "pastas_" + str(os.getpid()))
    dados = os.path.join(raiz, "dados")
    filha = os.path.join(dados, "a_pedagogia 'Á'")
    nome = 'Guia "Á".pdf'
    arquivo = os.path.join(filha, nome)
    config = os.path.join(raiz, "preferencias.json")
    os.makedirs(filha)
    os.mkdir(os.path.join(dados, "z_vazia"))
    os.symlink(filha, os.path.join(dados, "atalho"))
    with open(arquivo, "wb") as destino:
        destino.write(b"Conteudo que nao deve ser aberto pela navegacao")

    def rodar(argumentos, respostas=()):
        saida = StringIO()
        with patch.object(sys, "argv", ["main.py", "--config", config,
                                        "--sem-salvar", *argumentos]), \
                patch("builtins.input", side_effect=respostas), redirect_stdout(saida):
            interface.main()
        return saida.getvalue()

    try:
        assert pastas.carregar_ultimo_caminho(config) is None
        assert pastas.salvar_ultimo_caminho(filha, config) == filha
        assert pastas.carregar_ultimo_caminho(config) == filha
        with open(config, encoding="utf-8") as destino:
            assert json.load(destino) == {"versao": 1, "ultimo_caminho": filha}
        with patch.object(pastas, "carregar_ultimo_caminho", side_effect=AssertionError("Leu preferências")):
            assert pastas.raiz_inicial(dados, config) == dados
            assert pastas.raiz_inicial(None, config, usar_ultima=False) == pastas.RAIZ_PADRAO

        with open(config, "rb") as destino:
            anterior = destino.read()
        with patch.object(pastas.os, "replace", side_effect=OSError("Falha simulada")):
            try:
                pastas.salvar_ultimo_caminho(dados, config)
            except OSError:
                pass
            else:
                raise AssertionError("Falha de escrita não foi propagada")
        with open(config, "rb") as destino:
            assert destino.read() == anterior
        assert not any(n.endswith(".tmp") for n in os.listdir(raiz))
        colisao = f"{config}.{os.getpid()}.123.tmp"
        with open(colisao, "w") as destino:
            destino.write("Preservar temporario preexistente")
        with patch.object(pastas.time, "time_ns", return_value=123):
            try:
                pastas.salvar_ultimo_caminho(dados, config)
            except FileExistsError:
                pass
            else:
                raise AssertionError("Temporário preexistente foi sobrescrito")
        with open(colisao) as destino:
            assert destino.read() == "Preservar temporario preexistente"
        os.unlink(colisao)

        for invalido in ([], {"versao": True, "ultimo_caminho": filha},
                         {"versao": 2, "ultimo_caminho": filha},
                         {"versao": 1, "ultimo_caminho": "relativo"},
                         {"versao": 1, "ultimo_caminho": os.path.join(raiz, "ausente")}):
            with open(config, "w") as destino:
                json.dump(invalido, destino)
            with redirect_stdout(StringIO()):
                assert pastas.raiz_inicial(None, config) == pastas.RAIZ_PADRAO
        with open(config, "w") as destino:
            destino.write("{incompleto")
        with redirect_stdout(StringIO()):
            assert pastas.raiz_inicial(None, config) == pastas.RAIZ_PADRAO
        pastas.salvar_ultimo_caminho(dados, config)
        link_config = os.path.join(raiz, "config_link.json")
        os.symlink(config, link_config)
        try:
            pastas.salvar_ultimo_caminho(filha, link_config)
        except ValueError:
            pass
        else:
            raise AssertionError("Preferências seguiram symlink")
        with patch.object(pastas, "salvar_ultimo_caminho", side_effect=OSError("Somente leitura")), \
                redirect_stdout(StringIO()) as saida:
            assert pastas.lembrar_pasta(dados, config) == dados
            assert "Aviso" in saida.getvalue()
        protegido = os.path.join(raiz, "preservar.txt")
        with open(protegido, "w") as destino:
            destino.write("Preservar arquivo que nao e JSON")
        try:
            pastas.salvar_ultimo_caminho(dados, protegido)
        except ValueError:
            pass
        else:
            raise AssertionError("Preferências sobrescreveram arquivo de outro tipo")
        with open(protegido) as destino:
            assert destino.read() == "Preservar arquivo que nao e JSON"

        for respostas, esperado in ((["1", "1"], (filha, nome)),
                                    (["1", "..", "u"], (dados, None)),
                                    (["p", filha, "u"], (filha, None)),
                                    (["-1", "999", "abc", "0"], None),
                                    (["p", os.path.join(dados, "atalho"), "0"], None)):
            with patch("builtins.input", side_effect=respostas), \
                    patch("builtins.open", side_effect=AssertionError("Navegação abriu arquivo")), \
                    redirect_stdout(StringIO()) as saida:
                assert pastas.navegar_terminal(dados) == esperado
                assert "[pasta] 'atalho'" not in saida.getvalue()

        macos = SimpleNamespace(sysname="Darwin")
        with patch.object(pastas.os, "name", "posix"), \
                patch.object(pastas.os, "uname", return_value=macos, create=True), \
                patch.object(pastas.subprocess, "run", return_value=SimpleNamespace(stdout=filha + "/\n")) as dialogo:
            assert pastas.abrir_seletor(filha) == filha
            comando = dialogo.call_args.args[0]
            assert comando[-1] == filha and filha not in comando[2]
            assert dialogo.call_args.kwargs["check"] is True
            dialogo.return_value.stdout = "\n"
            assert pastas.abrir_seletor(filha) is None

        class FalhaTk(Exception):
            pass

        janela = Mock()
        escolher = Mock(return_value=filha)
        tk = SimpleNamespace(Tk=Mock(return_value=janela), TclError=FalhaTk,
                             filedialog=SimpleNamespace(askdirectory=escolher))
        with patch.dict(sys.modules, {"tkinter": tk}):
            assert pastas._dialogo_tk(dados) == filha
            janela.withdraw.assert_called_once()
            janela.destroy.assert_called_once()
            assert escolher.call_args.kwargs["mustexist"] is True
            janela.reset_mock()
            escolher.side_effect = FalhaTk("Sem ambiente gráfico")
            try:
                pastas._dialogo_tk(dados)
            except RuntimeError:
                janela.destroy.assert_called_once()
            else:
                raise AssertionError("Falha Tk não foi reportada")
        with patch.object(pastas, "abrir_seletor", side_effect=RuntimeError("Sem GUI")), \
                patch.object(pastas, "navegar_terminal", return_value=(dados, None)) as terminal, \
                redirect_stdout(StringIO()):
            assert pastas.selecionar_pasta(dados) == (dados, None)
            terminal.assert_called_once_with(dados)

        rodar(["--raiz", dados], ["0"])
        assert pastas.carregar_ultimo_caminho(config) == dados
        texto = rodar([], ["9", "1", "1", "1", "1", ""])
        assert arquivo in texto and "Arquivos processados/lidos: 0" in texto
        assert pastas.carregar_ultimo_caminho(config) == filha
        with open(config, "rb") as destino:
            anterior = destino.read()
        with patch.object(pastas, "abrir_seletor", return_value=None):
            rodar([], ["8", "1", "0"])
            assert "Seleção cancelada" in rodar(["--selecionar-pasta", "--etapa", "1"])
        with open(config, "rb") as destino:
            assert destino.read() == anterior
        with patch.object(pastas, "abrir_seletor", return_value=filha):
            texto = rodar(["--selecionar-pasta", "--etapa", "2", "--alvo", "Guia"])
            assert "Guia" in texto and "Métricas principais" in texto
        with patch.object(interface, "executar", return_value=([], Metricas())) as busca:
            rodar(["--algoritmo", "bfs", "--modo", "nome", "--alvo", "alvo"])
            assert busca.call_args.args[0] == pastas.RAIZ_PADRAO
        with patch.object(interface, "selecionar_pasta", side_effect=AssertionError("Abriu GUI")), \
                redirect_stderr(StringIO()):
            try:
                rodar(["--selecionar-pasta", "--etapa", "1", "--alvo", "incompatível"])
            except SystemExit as erro:
                assert erro.code == 2
            else:
                raise AssertionError("Opções inválidas abriram diálogo")
        print("OK: preferência JSON, falhas/colisões sem perda, cancelamento e restauração.")
        print("OK: navegação sem abrir conteúdos, symlinks excluídos e alvo sugerido no menu.")
        print("OK: adaptadores nativos macOS/Tk simulados, fallback e CLI reprodutível sem preferências implícitas.")
    finally:
        for pasta, dirs, arquivos in os.walk(raiz, topdown=False):
            for nome_arquivo in arquivos:
                os.unlink(os.path.join(pasta, nome_arquivo))
            for nome_pasta in dirs:
                caminho = os.path.join(pasta, nome_pasta)
                os.unlink(caminho) if os.path.islink(caminho) else os.rmdir(caminho)
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
