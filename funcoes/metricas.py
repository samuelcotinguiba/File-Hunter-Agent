"""Contadores e medições independentes de tempo e memória."""

from dataclasses import dataclass
import time
import tracemalloc


ROTULOS_PRINCIPAIS = (
    "Nós expandidos (N)",
    "Arquivos/Itens examinados",
    "Arquivos processados/lidos",
    "Custo do Caminho g(n)",
    "Consumo de Memória — Pico (KiB), tracemalloc",
    "Tempo de Execução (ms)",
)


@dataclass
class Metricas:
    """Estatísticas de uma execução; pico de alocações Python em KiB, tempo em ms.

    N=pastas_abertas; itens_examinados inclui arquivos e subpastas listados;
    arquivos_lidos conta arquivos cujo conteúdo foi processado, sem confundir
    essas leituras com acessos físicos ao disco. g mede somente o caminho final.
    """

    pastas_abertas: int = 0
    itens_examinados: int = 0
    arquivos_encontrados: int = 0
    arquivos_lidos: int = 0
    custo_g: int = 0
    tempo_ms: float = 0.0
    pico_mem_kb: float = 0.0

    @property
    def nos_expandidos(self):
        """Alias de N, mantendo o campo original pastas_abertas no JSON/API."""
        return self.pastas_abertas


def metricas_principais(metricas, modo):
    """Apresente os padrões obrigatórios sem duplicar contadores ou seus valores."""
    if modo not in ("nome", "conteudo"):
        raise ValueError("Modo deve ser nome ou conteudo.")
    m = vars(metricas) if isinstance(metricas, Metricas) else metricas
    unidade = "itens" if modo == "nome" else "bytes"
    valores = (m["pastas_abertas"], m["itens_examinados"], m["arquivos_lidos"],
               f'{m["custo_g"]} {unidade}', m["pico_mem_kb"], m["tempo_ms"])
    return dict(zip(ROTULOS_PRINCIPAIS, valores))


def metodologia_medicao():
    """Descreva métodos e unidades realmente usados, sem apresentar heap como RSS."""
    return {
        "tempo": {"funcao": "time.perf_counter", "unidade": "ms"},
        "memoria": {"funcao": "tracemalloc.get_traced_memory",
                    "tipo": "pico_alocacoes_python", "unidade": "KiB"},
        "execucoes_separadas": True,
        "contadores_por_execucao": True,
    }


def medir_tempo(funcao, *args, **kwargs):
    """Execute uma vez e retorne (resultado, ms), sem tracemalloc ativo."""
    if tracemalloc.is_tracing():
        raise RuntimeError("Desative tracemalloc antes de medir tempo.")
    inicio = time.perf_counter()
    resultado = funcao(*args, **kwargs)
    return resultado, (time.perf_counter() - inicio) * 1000


def medir_memoria(funcao, *args, **kwargs):
    """Execute uma vez e retorne (resultado, pico em KiB), sem medir tempo.

    Inclui alocações Python da chamada e de seu resultado. Não mede RSS.
    Use estado novo nesta chamada, separado da medição de tempo.
    """
    if tracemalloc.is_tracing():
        raise RuntimeError("Já existe uma sessão tracemalloc ativa.")
    tracemalloc.start()
    try:
        resultado = funcao(*args, **kwargs)
        _, pico = tracemalloc.get_traced_memory()
        return resultado, pico / 1024
    finally:
        tracemalloc.stop()
