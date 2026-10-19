"""Visualização opcional: isolamento, grupos comparáveis, PNGs e falhas de saída."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import main as interface
from funcoes.metricas import Metricas
from funcoes.relatorio import criar_registro
from funcoes import visualizacao


def main():
    """Verifique ausência da dependência e, quando instalada, exportação real com Agg."""
    with TemporaryDirectory(prefix="file_hunter_visualizacao_") as pasta:
        raiz = Path(pasta).resolve()
        pasta = str(raiz)
        ucs = criar_registro(pasta, "algoritmo", "ucs", "conteudo",
                             [str(raiz / "alvo.txt")],
                             Metricas(2, 4, 1, 2, 9, 1.5, 2.5), etapa=3)
        astar = json.loads(json.dumps(ucs))
        astar["parametros"].update(algoritmo="astar", alfa=100.0)
        astar["metricas"].update(pastas_abertas=1, arquivos_lidos=1)
        registros = [astar, ucs]
        copia = json.dumps(registros, sort_keys=True)
        grupos = visualizacao.agrupar_resultados(registros)
        assert [r["parametros"]["algoritmo"] for r in grupos[0]] == ["ucs", "astar"]
        for campo, valor in (("raiz", str(raiz / "outra")), ("alvo", "outro"),
                             ("extensoes_texto", [".txt"]), ("extrator_pdf", "outro")):
            outro = json.loads(json.dumps(astar))
            outro["parametros"][campo] = valor
            assert len(visualizacao.agrupar_resultados([ucs, outro])) == 2
        outro = json.loads(json.dumps(astar))
        outro["experimento"] = "outro"
        assert len(visualizacao.agrupar_resultados([ucs, outro])) == 2
        for invalido in ([], [ucs, ucs]):
            try:
                visualizacao.agrupar_resultados(invalido)
            except ValueError:
                pass
            else:
                raise AssertionError("Grupo vazio ou algoritmo duplicado foi aceito")
        with patch.dict(sys.modules, {"matplotlib.figure": None,
                                     "matplotlib.backends.backend_agg": None}):
            try:
                visualizacao.gerar_graficos(registros, raiz / "ausente")
            except RuntimeError as erro:
                assert "opcional Matplotlib" in str(erro) and "requirements-visualizacao.txt" in str(erro)
            else:
                raise AssertionError("Ausência de Matplotlib foi ignorada")
            assert not (raiz / "ausente").exists()

        def rodar(argumentos, respostas=()):
            saida = StringIO()
            with patch.object(sys, "argv", ["main.py", "--config", str(raiz / "config.json"),
                                            *argumentos]), \
                    patch("builtins.input", side_effect=respostas), redirect_stdout(saida):
                interface.main()
            return saida.getvalue()

        with patch.object(interface, "_exportar_graficos") as exportar, \
                patch.object(interface, "raiz_inicial", side_effect=AssertionError("Selecionou raiz")):
            rodar(["--graficos", "entrada.json", "--saida-graficos", "saida"])
            exportar.assert_called_once_with(["entrada.json"], "saida")
        with patch.object(visualizacao, "verificar_dependencia", side_effect=RuntimeError("Instale Matplotlib")):
            texto = rodar([], ("10", "0"))
            assert "opcional; requer Matplotlib" in texto and "Instale Matplotlib" in texto
        with patch.object(visualizacao, "verificar_dependencia"), \
                patch.object(interface, "_exportar_graficos") as exportar:
            rodar([], ("10", "entrada.json", "saida", "0"))
            exportar.assert_called_once_with(["entrada.json"], "saida")
        for argumentos in (["--graficos", "entrada.json", "--etapa", "1"],
                           ["--graficos", "entrada.json", "--alvo", "livro"],
                           ["--graficos", "entrada.json", "--sem-salvar"],
                           ["--saida-graficos", "saida"]):
            with redirect_stderr(StringIO()):
                try:
                    rodar(argumentos)
                except SystemExit as erro:
                    assert erro.code == 2
                else:
                    raise AssertionError("Opções de gráficos incompatíveis foram aceitas")

        codigo = ("import sys; from main import executar_etapa; "
                  "executar_etapa(1, sys.argv[1]); "
                  "assert not any(m == 'matplotlib' or m.startswith('matplotlib.') for m in sys.modules)")
        subprocess.run([sys.executable, "-c", codigo, pasta], check=True,
                       capture_output=True, text=True)
        try:
            Figure, Canvas = visualizacao.verificar_dependencia()
        except RuntimeError:
            print("OK: gráficos opcionais, grupos, menu/CLI e isolamento; renderização indisponível sem Matplotlib.")
            return

        figura = visualizacao._figura(grupos[0], Figure, Canvas)
        try:
            assert len(figura.axes) == 6
            for eixo, esperados in zip(figura.axes, ((2, 1), (4, 4), (2, 1), (9, 9), (2.5, 2.5), (1.5, 1.5))):
                assert tuple(b.get_height() for b in eixo.patches) == esperados
                assert eixo.get_ylim()[0] == 0 and eixo.get_ylim()[1] > max(esperados)
        finally:
            figura.clear()
        ausente = json.loads(json.dumps(ucs))
        ausente["encontrados"] = []
        ausente["metricas"].update(custo_g=0, arquivos_encontrados=0)
        ausente["avaliacao_final"] = None
        mapeamento = criar_registro(pasta, None, "bfs", "nome", [], Metricas(1), etapa=1)
        for registro, esperado in ((ausente, "Não encontrado"), (mapeamento, "Não se aplica")):
            figura = visualizacao._figura([registro], Figure, Canvas)
            try:
                assert not figura.axes[3].patches
                assert esperado in [t.get_text() for t in figura.axes[3].texts]
                minimo, maximo = figura.axes[3].get_xlim()
                assert minimo < 0 < maximo
            finally:
                figura.clear()
        diretorio = raiz / "pngs"
        caminhos = visualizacao.gerar_graficos(registros + [mapeamento], diretorio)
        assert len(caminhos) == 2
        assert all(Path(c).read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for c in caminhos)
        assert json.dumps(registros, sort_keys=True) == copia
        protegido = diretorio / "grafico_123_42_0.png"
        protegido.write_bytes(b"preservar")
        with patch.object(visualizacao.time, "time_ns", return_value=123), \
                patch.object(visualizacao.os, "getpid", return_value=42):
            novo = visualizacao.gerar_graficos(registros, diretorio)
            assert novo == [str(diretorio / "grafico_123_42_1.png")]
        assert protegido.read_bytes() == b"preservar"
        falha = Mock()
        falha.savefig.side_effect = OSError("Falha simulada")
        with patch.object(visualizacao, "_figura", return_value=falha):
            try:
                visualizacao.gerar_graficos(registros, raiz / "falha")
            except OSError:
                pass
            else:
                raise AssertionError("Falha ao exportar foi ignorada")
        falha.clear.assert_called_once()
        assert not list((raiz / "falha").iterdir())
        print("OK: seis métricas/unidades, PNGs reais, grupos separados, custo ausente, colisão e limpeza em falha.")


if __name__ == "__main__":
    main()
