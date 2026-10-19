"""Verificações de persistência, esquema e relatório sem novas buscas."""

import json
import os

from funcoes import relatorio
from main import executar


def main():
    """Valide ida e volta de oito buscas, colisões e JSONs inválidos."""
    raiz = os.path.join(os.getcwd(), "tests", "relatorio_" + str(os.getpid()))
    os.mkdir(raiz)
    dados = os.path.join(raiz, "dados")
    saida = os.path.join(raiz, "resultados")
    os.mkdir(dados)
    try:
        with open(os.path.join(dados, "algoritmo.txt"), "w", encoding="utf-8") as arquivo:
            arquivo.write("Um ALGORITMO de busca.\n")
        with open(os.path.join(dados, "foto.png"), "wb") as arquivo:
            arquivo.write(b"algoritmo")
        caminhos_json = []
        for modo in ("nome", "conteudo"):
            for algoritmo in ("bfs", "dfs", "ucs", "astar"):
                caminhos, metricas = executar(dados, "ALGORITMO", algoritmo, modo, alfa=2)
                caminho = relatorio.salvar_execucao(dados, "ALGORITMO", algoritmo, modo,
                                                    caminhos, metricas, alfa=2, diretorio=saida)
                caminhos_json.append(caminho)
                with open(caminho, encoding="utf-8") as arquivo:
                    registro = json.load(arquivo)
                assert registro["metricas"] == vars(metricas)
                assert registro["encontrados"] == caminhos
                assert registro["parametros"]["alfa"] == (2 if algoritmo == "astar" else None)
                if modo == "conteudo":
                    assert ".csv" in registro["parametros"]["extensoes_texto"]
                else:
                    assert registro["parametros"]["extensoes_texto"] is None
        registros = relatorio.carregar_resultados([saida, caminhos_json[0]])
        assert len(registros) == 8
        texto = relatorio.gerar_markdown(registros)
        assert "Tempo de Execução (ms)" in texto and "Pico (KiB)" in texto
        assert "Nós expandidos (N)" in texto and "Arquivos processados/lidos" in texto
        assert "bytes" in texto and "itens" in texto
        assert "não garante custo mínimo" in texto
        assert "Extensões de texto" in texto
        antigo = json.loads(json.dumps(registros[-1]))
        antigo["parametros"].pop("extensoes_texto")
        assert "não registrado" in relatorio.gerar_markdown([antigo])
        registro = registros[0]
        registro["parametros"]["alvo"] = "a|b\r\n<script>_`"
        texto = relatorio.gerar_markdown([registro])
        assert "a&#124;b<br>&lt;script&gt;\\_&#96;" in texto
        assert "<script>" not in texto
        for campo, valor in (("pastas_abertas", True), ("itens_examinados", -1),
                             ("tempo_ms", float("nan")), ("pico_mem_kb", float("inf")),
                             ("custo_g", "zero")):
            invalido = json.loads(json.dumps(registro))
            invalido["metricas"][campo] = valor
            try:
                relatorio.validar_registro(invalido)
            except ValueError:
                pass
            else:
                raise AssertionError(f"Métrica inválida aceita: {campo}")
        ruim = os.path.join(saida, "invalido.json")
        with open(ruim, "w") as arquivo:
            arquivo.write("{incompleto")
        try:
            relatorio.carregar_resultados([saida])
        except ValueError as erro:
            assert ruim in str(erro)
        else:
            raise AssertionError("JSON corrompido aceito")
        os.unlink(ruim)
        link = os.path.join(saida, "link.json")
        os.symlink(caminhos_json[0], link)
        assert len(relatorio.carregar_resultados([saida])) == 8
        try:
            relatorio.carregar_resultados([link])
        except ValueError:
            pass
        else:
            raise AssertionError("Symlink explícito aceito")
        tempo_original = relatorio.time.time_ns
        relatorio.time.time_ns = lambda: 123
        try:
            caminhos, metricas = executar(dados, "ausente", "ucs")
            a = relatorio.salvar_execucao(dados, "ausente", "ucs", "nome", caminhos,
                                         metricas, diretorio=saida)
            b = relatorio.salvar_execucao(dados, "ausente", "ucs", "nome", caminhos,
                                         metricas, diretorio=saida)
        finally:
            relatorio.time.time_ns = tempo_original
        assert a != b
        assert relatorio.carregar_resultados([a])[0]["encontrados"] == []
        try:
            relatorio.carregar_resultados([dados])
        except ValueError:
            pass
        else:
            raise AssertionError("Diretório sem JSON aceito")
        print("OK: oito buscas -> JSON -> Markdown; colisões, esquema, escapes e arquivos inválidos.")
    finally:
        for pasta, dirs, arquivos in os.walk(raiz, topdown=False):
            for nome in arquivos:
                os.unlink(os.path.join(pasta, nome))
            for nome in dirs:
                os.rmdir(os.path.join(pasta, nome))
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
