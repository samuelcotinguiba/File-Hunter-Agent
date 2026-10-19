"""Sessão guiada, comparações sequenciais, retorno e reaproveitamento de resultados."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

import main as programa
from funcoes import interface


def main():
    """Exercite a interface com buscas reais pequenas, sem diálogos ou PDFs grandes."""
    with TemporaryDirectory(prefix="file_hunter_interface_") as temporaria:
        base = Path(temporaria).resolve()
        dados = base / "dados"
        (dados / "a_pedagogia").mkdir(parents=True)
        (dados / "z_outra").mkdir()
        (dados / "inicio.txt").write_text("Introducao", encoding="utf-8")
        (dados / "a_pedagogia" / "livro_aula.md").write_text("Algoritmo e pedagogia", encoding="utf-8")
        (dados / "z_outra" / "livro_curto.txt").write_text("Algoritmo", encoding="utf-8")
        config = str(base / "config.json")
        resultados = base / "resultados"

        def rodar(respostas=(), argumentos=(), salvar=False, usar_raiz=True):
            saida = StringIO()
            opcoes = ["main.py", *(["--raiz", str(dados)] if usar_raiz else []), "--config", config,
                      "--resultados", str(resultados), *argumentos]
            if not salvar:
                opcoes.append("--sem-salvar")
            with patch.object(sys, "argv", opcoes), \
                    patch("builtins.input", side_effect=respostas) as entrada, redirect_stdout(saida):
                programa.main()
            return saida.getvalue(), entrada

        with patch.object(programa, "executar_etapa", wraps=programa.executar_etapa) as executar:
            texto, entrada = rodar(("", "p", "", "p", "", "n"))
            assert [c.args[:3] for c in executar.call_args_list] == [
                (1, str(dados), None), (2, str(dados), "livro"), (3, str(dados), "algoritmo")]
            assert entrada.call_count == 6
            assert all(f"Etapa {e} concluída" in texto for e in (1, 2, 3))
            assert "[Tempo 1/4] BFS" in texto and "[Memória 2/2] A*" in texto
            assert "Algoritmo: " not in texto and "1. Nome  2. Conteúdo" not in texto
            assert any("Deseja voltar ao menu?" in c.args[0] for c in entrada.call_args_list)
            assert not resultados.exists()
        with open(config, encoding="utf-8") as arquivo:
            assert json.load(arquivo)["ultimo_caminho"] == str(dados)

        with patch.object(programa, "executar_etapa", wraps=programa.executar_etapa) as executar:
            texto, entrada = rodar(("2", "aula", "s", "2", "", "n"))
            assert [c.args[2] for c in executar.call_args_list] == ["aula", "aula"]
            assert texto.count("File Hunter Agent — Comparações") == 2
            assert any("Palavra no nome [aula]" in c.args[0] for c in entrada.call_args_list)

        with patch.object(programa, "executar_etapa", wraps=programa.executar_etapa) as executar, \
                patch.object(interface, "exportar_registros") as exportar:
            texto, _ = rodar(("1", "r", "g", "n"))
            assert executar.call_count == 1 and exportar.call_count == 1
            registros, destino = exportar.call_args.args
            assert [r["parametros"]["algoritmo"] for r in registros] == ["bfs", "dfs"]
            assert destino == str(resultados / "graficos")
            assert "Todos os arquivos na ordem de descoberta" in texto
            assert not resultados.exists()

        texto, _ = rodar(("1", "n"), salvar=True)
        completo = (resultados / "etapa_1.md").read_text(encoding="utf-8")
        assert "primeiros 10" in texto and "Todos os arquivos na ordem de descoberta" not in texto
        assert "Percurso de expansão dos diretórios" not in texto
        assert "Todos os arquivos na ordem de descoberta" in completo
        assert "Percurso de expansão dos diretórios" in completo
        arquivos = list(resultados.glob("*.json"))
        assert len(arquivos) == 2
        assert all(len(json.loads(p.read_text())["encontrados"]) == 3 for p in arquivos)

        with patch.object(programa, "executar_etapa", wraps=programa.executar_etapa) as executar:
            rodar(("5", "3", "100", "2", "", "n"))
            assert executar.call_args.args[3] == 100
        texto, _ = rodar(("5", "3", "nan", "s", "1", "n"))
        assert "Não foi possível concluir" in texto and "Etapa 1 concluída" in texto

        chamada_real = programa.executar_etapa
        tentativas = []

        def falhar_uma_vez(*args, **kwargs):
            tentativas.append(args)
            if len(tentativas) == 1:
                raise OSError("Leitura recusada")
            return chamada_real(*args, **kwargs)

        with patch.object(programa, "executar_etapa", side_effect=falhar_uma_vez):
            texto, _ = rodar(("1", "s", "1", "n"))
            assert "Leitura recusada" in texto and texto.count("Etapa 1 concluída") == 1
            assert len(tentativas) == 2
        texto, _ = rodar(("invalida", "1", "invalida", "n"))
        assert texto.count("Opção inválida") == 2
        texto, entrada = rodar(argumentos=("--etapa", "1"))
        assert not entrada.called and "Deseja voltar ao menu?" not in texto
        assert "Todos os arquivos na ordem de descoberta" in texto
        with patch.object(programa, "raiz_inicial", return_value=str(base / "ausente")), \
                patch.object(interface, "menu_pastas", return_value=(str(dados), None)) as selecionar:
            texto, _ = rodar(("1", "n"), usar_raiz=False)
            selecionar.assert_called_once()
            assert "Etapa 1 concluída" in texto
        print("OK: três comparações em seis respostas, retorno ao menu, termos/pasta preservados,")
        print("gráfico/relatório sem nova busca, entrega completa salva, alfa, erros e CLI sem perguntas extras.")


if __name__ == "__main__":
    main()
