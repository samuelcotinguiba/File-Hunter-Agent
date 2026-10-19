"""Entregas completas e separadas: descoberta global, nome e conteúdo."""

import json
import os

from funcoes.bfs_dfs import mapear
from funcoes.relatorio import (carregar_resultados, gerar_relatorio_etapa, salvar_registro,
                               validar_registro)
from main import executar_etapa


def main():
    """Compare cronologias conhecidas e custos por caminho sem relistar no relatório."""
    raiz = os.path.join(os.getcwd(), "tests", "etapas_" + str(os.getpid()))
    dados = os.path.join(raiz, "dados")
    saida = os.path.join(raiz, "resultados")
    os.makedirs(os.path.join(dados, "a_livro", "profunda"))
    os.mkdir(os.path.join(dados, "b"))
    nomes = ("0_inicio.txt", "a_livro/0_livro.md", "a_livro/1_livro.txt",
             "a_livro/profunda/livro_fundo.txt", "b/livro_curto.txt")
    try:
        for i, nome in enumerate(nomes):
            with open(os.path.join(dados, nome), "w") as arquivo:
                arquivo.write("sem alvo" if i == 0 else "algoritmo")
        os.symlink(dados, os.path.join(dados, "a_livro", "ciclo"))
        etapa1 = executar_etapa(1, dados)
        bfs, dfs = etapa1
        assert bfs["encontrados"] == [os.path.join(dados, nomes[i]) for i in (0, 1, 2, 4, 3)]
        assert dfs["encontrados"] == [os.path.join(dados, nomes[i]) for i in (0, 1, 2, 3, 4)]
        assert bfs["primeiros_10"] == bfs["encontrados"]
        assert bfs["experimento"] == dfs["experimento"]
        for r in etapa1:
            validar_registro(r)
            assert r["parametros"]["alvo"] is None and r["parametros"]["escopo"] == "mapeamento"
            m = r["metricas"]
            assert (m["pastas_abertas"], m["arquivos_encontrados"], m["itens_examinados"], m["arquivos_lidos"], m["custo_g"]) == (4, 5, 8, 0, 0)
            assert len(r["expansoes"]) == 4
            salvar_registro(r, saida)
        texto1 = gerar_relatorio_etapa(carregar_resultados([saida]), 1)
        assert "primeiros 10" in texto1 and "Todos os arquivos na ordem" in texto1
        assert "./tests/" in texto1 and "Não se aplica (mapeamento)" in texto1
        assert "Pico de Memória (KB)" in texto1
        for algoritmo in ("bfs", "dfs"):
            duplicado = next(r for r in etapa1 if r["parametros"]["algoritmo"] == algoritmo)
            try:
                gerar_relatorio_etapa(etapa1 + [duplicado], 1)
            except ValueError as erro:
                assert algoritmo.upper() in str(erro) and "JSON" in str(erro)
            else:
                raise AssertionError("Primeiros 10 aceitaram mais de uma execução do mesmo algoritmo")
            outro = json.loads(json.dumps(duplicado))
            outro["experimento"] += "_outro"
            texto_separado = gerar_relatorio_etapa(etapa1 + [outro], 1)
            assert texto_separado.count("Experimento:") == 2
        amostra = json.loads(json.dumps(etapa1))
        amostra[0]["metricas"]["pico_mem_kb"] = 1.0
        assert "1.024" in gerar_relatorio_etapa(amostra, 1)
        etapa2 = executar_etapa(2, dados, alfa=100)
        assert [r["parametros"]["algoritmo"] for r in etapa2] == ["bfs", "dfs", "ucs", "astar"]
        assert [r["metricas"]["custo_g"] for r in etapa2] == [6, 6, 4, 6]
        assert [r["metricas"]["pastas_abertas"] for r in etapa2] == [2, 2, 3, 2]
        assert all(len(r["encontrados"]) == 1 and r["metricas"]["arquivos_lidos"] == 0 for r in etapa2)
        assert etapa2[0]["encontrados"] == [os.path.join(dados, "a_livro", "0_livro.md")]
        assert etapa2[0]["metricas"]["arquivos_encontrados"] == 2
        texto2 = gerar_relatorio_etapa(etapa2, 2)
        assert "Alvo Solicitado" in texto2 and "Custo Acumulado g(n)" in texto2
        assert "Análise do custo acumulado" in texto2 and "Custo local (itens)" in texto2
        assert "Percurso de expansão" in texto2 and "Diferença UCS − A*" in texto2
        etapa3 = executar_etapa(3, dados, alfa=100)
        assert [r["parametros"]["algoritmo"] for r in etapa3] == ["ucs", "astar"]
        assert [r["metricas"]["custo_g"] for r in etapa3] == [17, 26]
        assert [r["metricas"]["arquivos_lidos"] for r in etapa3] == [4, 3]
        texto3 = gerar_relatorio_etapa(etapa3, 3)
        assert "Jaccard de bigramas" in texto3 and "Redução de expansões/leituras" in texto3
        assert "Arquivos Lidos do Disco" in texto3 and "g do diretório" in texto3
        ausentes = executar_etapa(2, dados, alvo="ausente")
        assert all(r["metricas"]["pastas_abertas"] == 4 and not r["encontrados"] for r in ausentes)
        assert "Não encontrado" in gerar_relatorio_etapa(ausentes, 2, "ausente")
        invalido = json.loads(json.dumps(etapa2[0]))
        invalido["expansoes"][0]["g"] += 1
        try:
            validar_registro(invalido)
        except ValueError:
            pass
        else:
            raise AssertionError("g incompatível com o rastro foi aceito")
        try:
            mapear(dados, "ucs")
        except ValueError:
            pass
        else:
            raise AssertionError("UCS recebeu modo global")
        with open(os.path.join(dados, "livro.pdf"), "wb") as arquivo:
            arquivo.write(b"fixture somente para nome")
        assert all(r["metricas"]["arquivos_encontrados"] == 6 for r in executar_etapa(1, dados))
        assert all(r["encontrados"] == [os.path.join(dados, "livro.pdf")] for r in executar_etapa(2, dados, ".pdf"))
        for i in range(12):
            with open(os.path.join(dados, f"extra_{i:02d}.txt"), "w") as arquivo:
                arquivo.write("sem alvo")
        for r in executar_etapa(1, dados):
            assert len(r["encontrados"]) == 18
            assert len(r["primeiros_10"]) == 10 and r["primeiros_10"] == r["encontrados"][:10]
        vazio = os.path.join(raiz, "vazio")
        os.mkdir(vazio)
        assert all(r["metricas"]["pastas_abertas"] == 1 and not r["encontrados"] for r in executar_etapa(1, vazio))
        print("OK: mapeamento só BFS/DFS, cronologias completas, primeiro alvo, quatro buscas por nome,")
        print("custos 6/6/4/6 itens, conteúdo 17/26 bytes, rastros, relatórios, ciclos e ausência.")
    finally:
        for pasta, dirs, arquivos in os.walk(raiz, topdown=False):
            for nome in arquivos:
                os.unlink(os.path.join(pasta, nome))
            for nome in dirs:
                caminho = os.path.join(pasta, nome)
                if os.path.islink(caminho):
                    os.unlink(caminho)
                else:
                    os.rmdir(caminho)
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
