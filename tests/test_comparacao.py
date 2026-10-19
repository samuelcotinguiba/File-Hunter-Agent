"""Tabela da etapa 3: filtros, custos finais, caminhos e comparação sequencial."""

import json
import os

from funcoes.relatorio import criar_registro, gerar_markdown, gerar_tabela_comparativa
from main import comparar_conteudo, executar


def main():
    """Confira sete colunas, custo do objetivo, ausência e grupos incompatíveis."""
    raiz = os.path.join(os.getcwd(), "tests", "comparacao_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        for pasta, dados in (("algoritmo", "Algoritmo" + "x" * 100), ("zz", "Algoritmo")):
            os.mkdir(os.path.join(raiz, pasta))
            with open(os.path.join(raiz, pasta, "documento.txt"), "w") as arquivo:
                arquivo.write(dados)
        registros = comparar_conteudo(raiz, alfa=1000)
        assert [r["parametros"]["algoritmo"] for r in registros] == ["ucs", "astar"]
        assert [r["metricas"]["custo_g"] for r in registros] == [9, 109]
        assert [r["metricas"]["arquivos_lidos"] for r in registros] == [2, 1]
        assert [r["avaliacao_final"]["f"] for r in registros] == [9, 109]
        assert all(r["avaliacao_final"]["h"] == 0 for r in registros)
        texto = gerar_tabela_comparativa(registros)
        cabecalho = "| Algoritmo | Palavra no Conteúdo | Caminho | Pastas Abertas | Arquivos Lidos do Disco | Custo Total f(n) | Tempo (ms) |"
        assert cabecalho in texto and "h=0 e f=g" in texto
        comparativo = texto.split("### Métricas principais")[0]
        linhas = [l for l in comparativo.splitlines() if l.startswith(("| UCS |", "| A\\* |"))]
        assert len(linhas) == 2 and all(len(l.split("|")) == 9 for l in linhas)
        assert "9 bytes" in linhas[0] and "109 bytes" in linhas[1]
        assert "/zz/documento.txt" in linhas[0]
        assert "Nós expandidos (N)" in texto and "tracemalloc" in texto
        assert "Tempo de Execução (ms)" in texto and "Custo do Caminho g(n)" in texto
        assert "Métricas comparativas" in gerar_markdown(registros)
        caminhos, metricas = executar(raiz, "algoritmo", "bfs", "conteudo")
        bfs = criar_registro(raiz, "algoritmo", "bfs", "conteudo", caminhos, metricas)
        assert gerar_tabela_comparativa(registros + [bfs]) == texto
        ausentes = comparar_conteudo(raiz, "ausente")
        texto_ausente = gerar_tabela_comparativa(ausentes, "ausente")
        comparativo_ausente = texto_ausente.split("### Métricas principais")[0]
        assert comparativo_ausente.count("Não encontrado") == 2 and "0 bytes" not in comparativo_ausente
        legado = json.loads(json.dumps(registros[1]))
        legado["parametros"].pop("extensoes_texto")
        legado.pop("avaliacao_final")
        separado = gerar_tabela_comparativa([registros[0], legado])
        assert separado.count(cabecalho) == 2 and "Comparação incompleta" in separado
        try:
            gerar_tabela_comparativa([bfs])
        except ValueError:
            pass
        else:
            raise AssertionError("Registro BFS aceito como comparação UCS/A*")
        print("OK: sete colunas, filtro UCS/A*, f final 9/109 bytes, caminhos, ausência e grupos.")
    finally:
        for pasta, dirs, arquivos in os.walk(raiz, topdown=False):
            for nome in arquivos:
                os.unlink(os.path.join(pasta, nome))
            for nome in dirs:
                os.rmdir(os.path.join(pasta, nome))
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
