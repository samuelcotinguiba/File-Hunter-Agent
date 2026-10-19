"""Contadores e medições independentes de tempo e memória."""

from dataclasses import dataclass
import time
import tracemalloc


@dataclass
class Metricas:
    """Estatísticas de uma execução; memória em KiB e tempo em ms."""

    pastas_abertas: int = 0
    itens_examinados: int = 0
    arquivos_encontrados: int = 0
    arquivos_lidos: int = 0
    custo_g: int = 0
    tempo_ms: float = 0.0
    pico_mem_kb: float = 0.0


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
