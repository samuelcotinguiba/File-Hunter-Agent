"""Verifique o escopo do timer e a ordem do lote sem depender de sleeps/cache."""

import json
import os
import tracemalloc

import main as interface
from funcoes import metricas
from funcoes.relatorio import (gerar_metricas_principais, gerar_relatorio_etapa,
                               validar_registro)


def main():
    """Separe tempo, perfil e registros com relógio virtual e estados distintos."""
    originais = (metricas.time.perf_counter, interface.buscar, interface.ucs,
                 interface.astar, interface.criar_registro)
    relogio = [100.0]
    eventos, estados = [], []
    falha = [None]
    raiz = os.getcwd()
    caminho = os.path.join(raiz, "main.py")

    def simular(algoritmo, modo, visitas):
        perfil = tracemalloc.is_tracing()
        eventos.append((algoritmo, "memoria" if perfil else "tempo"))
        # A busca demora 125 ms; o perfil simula 1000 segundos de sobrecarga.
        relogio[0] += 1000 if perfil else 0.125
        if perfil and falha[0] == "excecao":
            raise OSError("Falha simulada na leitura durante o perfil.")
        m = metricas.Metricas(pastas_abertas=1, itens_examinados=1,
                             arquivos_encontrados=1, custo_g=1,
                             arquivos_lidos=int(modo == "conteudo"))
        if perfil and falha[0] == "divergencia":
            m.itens_examinados += 1
        if visitas is not None:
            assert visitas == []
            visitas.append({"diretorio": raiz, "custo_local": 1, "g": 1})
        estados.append((m, visitas))
        return [caminho], m

    def busca_bfs_dfs(raiz, alvo, estrategia, modo, *, visitas=None):
        return simular(estrategia, modo, visitas)

    def busca_ucs(raiz, alvo, modo, *, visitas=None):
        return simular("ucs", modo, visitas)

    def busca_astar(raiz, alvo, modo, alfa, *, visitas=None):
        return simular("astar", modo, visitas)

    def criar_registro(*args, **kwargs):
        eventos.append((args[2], "registro"))
        relogio[0] += 500  # Trabalho da interface posterior às medições.
        return originais[4](*args, **kwargs)

    metricas.time.perf_counter = lambda: relogio[0]
    interface.buscar, interface.ucs, interface.astar = busca_bfs_dfs, busca_ucs, busca_astar
    interface.criar_registro = criar_registro
    try:
        for etapa, algoritmos in ((2, ("bfs", "dfs", "ucs", "astar")), (3, ("ucs", "astar"))):
            eventos.clear()
            estados.clear()
            registros = interface.executar_etapa(etapa, raiz)
            assert eventos == [(a, fase) for fase in ("tempo", "memoria", "registro") for a in algoritmos]
            assert len({id(m) for m, _ in estados}) == 2 * len(algoritmos)
            assert len({id(v) for _, v in estados}) == 2 * len(algoritmos)
            for r in registros:
                validar_registro(r)
                assert r["metricas"]["tempo_ms"] == 125.0
                assert r["metricas"]["pastas_abertas"] == 1  # Não soma as duas buscas.
                assert r["metricas"]["pico_mem_kb"] > 0
                assert r["protocolo_lote"] == metricas.PROTOCOLO_LOTE
            texto = gerar_relatorio_etapa(registros, etapa)
            assert "todos os tempos primeiro" in texto and "não há limpeza do cache" in texto
            antigo = json.loads(json.dumps(registros[0]))
            antigo.pop("protocolo_lote")
            validar_registro(antigo)
            misturados = [registros[0], antigo]
            assert gerar_relatorio_etapa(misturados, etapa).count("Comparação incompleta:") == 2
            assert "todos os tempos primeiro" in gerar_metricas_principais(iter(registros))
            assert "todos os tempos primeiro" not in gerar_metricas_principais(iter(misturados))
            invalido = dict(registros[0], protocolo_lote="tempo_com_tracemalloc")
            try:
                validar_registro(invalido)
            except ValueError:
                pass
            else:
                raise AssertionError("Protocolo incompatível foi aceito")
        eventos.clear()
        visitas = [{"anterior": True}]
        encontrados, m = interface.executar(raiz, "livro", "bfs", visitas=visitas)
        assert eventos == [("bfs", "tempo"), ("bfs", "memoria")]
        assert encontrados == [caminho] and m.tempo_ms == 125.0
        assert visitas == [{"diretorio": raiz, "custo_local": 1, "g": 1}]
        for motivo, tipo in (("divergencia", RuntimeError), ("excecao", OSError)):
            eventos.clear()
            falha[0] = motivo
            try:
                interface.executar_etapa(2, raiz)
            except tipo:
                pass
            else:
                raise AssertionError("Falha entre medições não foi propagada")
            assert not any(fase == "registro" for _, fase in eventos)
            assert not tracemalloc.is_tracing()
        print("OK: timer 125 ms mesmo com perfil de 1000 s e registro de 500 s simulados;")
        print("todos os tempos antes dos perfis, estados novos, divergência e falha sem publicar.")
        falha[0] = None
        avisos = []

        def progresso(fase, indice, total):
            assert not tracemalloc.is_tracing()
            avisos.append((fase, indice, total))
            relogio[0] += 250  # Impressão demorada deve ficar fora de tempo e pico.

        registros = interface.executar_etapa(3, raiz, progresso=progresso)
        assert avisos == [(fase, indice, 2) for fase in ("Tempo", "Memória") for indice in (1, 2)]
        assert all(r["metricas"]["tempo_ms"] == 125 for r in registros)
        print("OK: avisos de progresso também ficam fora do cronômetro e do tracemalloc.")
    finally:
        (metricas.time.perf_counter, interface.buscar, interface.ucs,
         interface.astar, interface.criar_registro) = originais


if __name__ == "__main__":
    main()
