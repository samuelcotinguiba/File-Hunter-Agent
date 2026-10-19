"""Padrões obrigatórios: N, itens/leitura, g, pico tracemalloc e perf_counter."""

import json
import os
import tracemalloc

from funcoes import metricas
from funcoes.relatorio import criar_registro, gerar_metricas_principais, validar_registro
from main import executar


def main():
    """Confira instrumentos, unidades, contagem independente e compatibilidade."""
    original = metricas.time.perf_counter
    instantes = iter((100.0, 100.125))
    metricas.time.perf_counter = lambda: next(instantes)
    try:
        def executar_sem_tracing():
            assert not tracemalloc.is_tracing()
            return "tempo"
        resultado, ms = metricas.medir_tempo(executar_sem_tracing)
        assert resultado == "tempo" and ms == 125.0
    finally:
        metricas.time.perf_counter = original

    def alocar():
        assert tracemalloc.is_tracing()
        return bytearray(512 * 1024)
    dados, pico = metricas.medir_memoria(alocar)
    assert pico >= len(dados) / 1024 and not tracemalloc.is_tracing()
    raiz = os.path.join(os.getcwd(), "tests", "metricas_" + str(os.getpid()))
    os.mkdir(raiz)
    try:
        for nome, conteudo in (("alvo.txt", "algoritmo"), ("apoio.md", "sem alvo")):
            with open(os.path.join(raiz, nome), "w") as arquivo:
                arquivo.write(conteudo)
        for modo, alvo, custo, lidos in (("nome", "alvo", 2, 0), ("conteudo", "algoritmo", 17, 2)):
            caminhos, m = executar(raiz, alvo, "bfs", modo)
            assert m.nos_expandidos == m.pastas_abertas == 1
            assert m.itens_examinados == 2 and m.arquivos_lidos == lidos
            assert m.custo_g == custo and m.tempo_ms >= 0 and m.pico_mem_kb > 0
            principais = metricas.metricas_principais(m, modo)
            assert principais["Nós expandidos (N)"] == 1
            assert principais["Arquivos/Itens examinados"] == 2
            assert principais["Arquivos processados/lidos"] == lidos
            assert principais["Custo do Caminho g(n)"] == f"{custo} " + ("itens" if modo == "nome" else "bytes")
            registro = criar_registro(raiz, alvo, "bfs", modo, caminhos, m)
            assert registro["medicao"]["tempo"]["funcao"] == "time.perf_counter"
            assert registro["medicao"]["memoria"]["tipo"] == "pico_alocacoes_python"
            assert registro["medicao"]["execucoes_separadas"] is True
            tabela = gerar_metricas_principais([registro])
            assert "Nós expandidos (N)" in tabela and "Consumo de Memória" in tabela
            assert "não RSS" in tabela and "time.perf_counter" in tabela
            antigo = json.loads(json.dumps(registro))
            antigo.pop("medicao")
            validar_registro(antigo)
            invalido = json.loads(json.dumps(registro))
            invalido["medicao"]["memoria"]["tipo"] = "RSS"
            try:
                validar_registro(invalido)
            except ValueError:
                pass
            else:
                raise AssertionError("RSS aceito como pico tracemalloc")
        print("OK: N e leituras por execução; g em itens/bytes; perf_counter em ms; pico tracemalloc em KiB.")
    finally:
        for nome in os.listdir(raiz):
            os.unlink(os.path.join(raiz, nome))
        os.rmdir(raiz)


if __name__ == "__main__":
    main()
