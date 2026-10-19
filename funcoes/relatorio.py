"""Persistência de execuções e conversão de JSON em tabelas Markdown."""

import argparse
import json
import os
import time

from .metricas import Metricas


def validar_registro(registro):
    """Valide o esquema v1 e rejeite métricas inválidas antes de usar o JSON."""
    if not isinstance(registro, dict) or type(registro.get("versao")) is not int or registro["versao"] != 1:
        raise ValueError("Registro deve usar o esquema versao=1.")
    if not isinstance(registro.get("instante_utc"), str) or not registro["instante_utc"]:
        raise ValueError("instante_utc ausente ou inválido.")
    parametros = registro.get("parametros")
    if not isinstance(parametros, dict):
        raise ValueError("Parâmetros ausentes ou inválidos.")
    for campo in ("raiz", "alvo"):
        if not isinstance(parametros.get(campo), str) or not parametros[campo]:
            raise ValueError(f"Parâmetro {campo} ausente ou inválido.")
    if parametros.get("algoritmo") not in ("bfs", "dfs", "ucs", "astar"):
        raise ValueError("Algoritmo inválido no registro.")
    if parametros.get("modo") not in ("nome", "conteudo"):
        raise ValueError("Modo inválido no registro.")
    alfa = parametros.get("alfa")
    if parametros["algoritmo"] == "astar":
        if type(alfa) not in (int, float) or not 0 <= alfa < float("inf"):
            raise ValueError("alfa deve ser finito e não negativo no A*.")
    elif alfa is not None:
        raise ValueError("alfa deve ser null fora do A*.")
    encontrados = registro.get("encontrados")
    if not isinstance(encontrados, list) or any(not isinstance(p, str) or not p for p in encontrados):
        raise ValueError("encontrados deve ser uma lista de caminhos.")
    metricas = registro.get("metricas")
    if not isinstance(metricas, dict):
        raise ValueError("Métricas ausentes ou inválidas.")
    for campo, padrao in vars(Metricas()).items():
        valor = metricas.get(campo)
        if isinstance(padrao, int):
            valido = type(valor) is int and valor >= 0
        else:
            valido = type(valor) in (int, float) and 0 <= valor < float("inf")
        if not valido:
            raise ValueError(f"Métrica {campo} deve ser numérica, finita e não negativa.")
    if metricas["arquivos_encontrados"] < len(encontrados):
        raise ValueError("Contador de encontrados menor que a lista retornada.")
    if not encontrados and metricas["custo_g"] != 0:
        raise ValueError("Registro sem resultado deve ter custo_g zero.")
    if parametros["modo"] == "nome" and metricas["arquivos_lidos"] != 0:
        raise ValueError("Busca por nome não deve ler arquivos.")
    return registro


def salvar_execucao(raiz, alvo, algoritmo, modo, encontrados, metricas,
                    alfa=1.0, diretorio="resultados"):
    """Salve um JSON exclusivo após as medições; retorne seu caminho absoluto.

    Serialização e disco ficam fora do tempo/pico das buscas. Nomes exclusivos
    evitam sobrescrever execuções anteriores, inclusive no mesmo nanossegundo.
    """
    registro = {
        "versao": 1,
        "instante_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parametros": {
            "raiz": os.path.realpath(raiz), "alvo": alvo,
            "algoritmo": algoritmo, "modo": modo,
            "alfa": alfa if algoritmo == "astar" else None,
        },
        "encontrados": list(encontrados),
        "metricas": vars(metricas).copy(),
    }
    validar_registro(registro)
    texto = json.dumps(registro, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    diretorio = os.path.abspath(diretorio)
    os.makedirs(diretorio, exist_ok=True)
    base = f"{time.time_ns()}_{os.getpid()}"
    contador = 0
    while True:
        caminho = os.path.join(diretorio, f"execucao_{base}_{contador}.json")
        try:
            arquivo = open(caminho, "x", encoding="utf-8")
        except FileExistsError:
            contador += 1
            continue
        try:
            with arquivo:
                arquivo.write(texto)
        except BaseException:
            os.unlink(caminho)
            raise
        return caminho


def carregar_resultados(entradas):
    """Leia arquivos JSON ou diretórios, em ordem estável e sem duplicá-los."""
    caminhos = []
    vistos = set()
    for entrada in entradas:
        if os.path.islink(entrada):
            raise ValueError(f"Entrada do relatório é symlink: {entrada}")
        if os.path.isdir(entrada):
            with os.scandir(entrada) as itens:
                candidatos = sorted(item.path for item in itens
                                    if item.name.endswith(".json")
                                    and item.is_file(follow_symlinks=False))
        else:
            candidatos = [os.fspath(entrada)]
        for caminho in candidatos:
            real = os.path.realpath(caminho)
            if real not in vistos:
                vistos.add(real)
                caminhos.append(caminho)
    registros = []
    for caminho in caminhos:
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                registro = validar_registro(json.load(arquivo))
        except (ValueError, UnicodeError) as erro:
            raise ValueError(f"JSON inválido em {caminho}: {erro}") from erro
        registro["origem_json"] = os.path.abspath(caminho)
        registros.append(registro)
    if not registros:
        raise ValueError("Nenhuma execução JSON encontrada.")
    return registros


def _celula(valor):
    """Preserve tabelas ao receber pipes, HTML, Markdown e quebras de linha."""
    texto = str(valor).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    texto = texto.replace("\\", "\\\\").replace("|", "&#124;").replace("`", "&#96;")
    texto = texto.replace("*", "\\*").replace("_", "\\_")
    return texto.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def gerar_markdown(registros):
    """Gere tabelas de parâmetros e métricas sem executar novas buscas."""
    if not registros:
        raise ValueError("Nenhuma execução para relatar.")
    for registro in registros:
        validar_registro(registro)
    linhas = [
        "# Relatório File Hunter Agent", "",
        "Compare execuções com a mesma raiz, alvo e modo. g usa itens no modo nome",
        "e bytes no modo conteúdo. Tempos e picos vêm de execuções separadas.", "",
        "## Parâmetros", "",
        "| ID | JSON | Algoritmo | Modo | Raiz | Alvo | Alfa |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for indice, registro in enumerate(registros, 1):
        p = registro["parametros"]
        campos = (indice, registro.get("origem_json", "—"), p["algoritmo"].upper(),
                  p["modo"], p["raiz"], p["alvo"], p.get("alfa") if p["algoritmo"] == "astar" else "—")
        linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
    linhas.extend([
        "", "## Métricas", "",
        "| ID | Retornados | Encontrados | Pastas abertas | Itens examinados | Arquivos lidos | g | Unidade | Tempo (ms) | Pico (KiB) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for indice, registro in enumerate(registros, 1):
        m = registro["metricas"]
        campos = (indice, len(registro["encontrados"]), m["arquivos_encontrados"],
                  m["pastas_abertas"], m["itens_examinados"], m["arquivos_lidos"],
                  m["custo_g"], "itens" if registro["parametros"]["modo"] == "nome" else "bytes",
                  f'{m["tempo_ms"]:.3f}', f'{m["pico_mem_kb"]:.3f}')
        linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
    linhas.extend([
        "", "Encontrados conta correspondências descobertas; retornados conta a pasta objetivo escolhida.",
        "Sem resultado, g é zero. Pastas e arquivos lidos contabilizam toda a exploração.",
        "A* usa heurística não admissível: não garante custo mínimo ou menor exploração.",
        "Pico mede alocações Python (KiB), não RSS. Cache do sistema e carga afetam o tempo.", "",
    ])
    return "\n".join(linhas)


def main():
    """Converta JSONs com python3 -m funcoes.relatorio ENTRADAS --saida arquivo.md."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entradas", nargs="+", help="Arquivos JSON ou diretórios")
    parser.add_argument("--saida", help="Arquivo .md; omitido, imprime o relatório")
    args = parser.parse_args()
    try:
        texto = gerar_markdown(carregar_resultados(args.entradas))
        if args.saida:
            if not args.saida.lower().endswith(".md"):
                raise ValueError("O arquivo de saída deve ter extensão .md.")
            # Não sobrescrever um JSON de entrada através de um link simbólico.
            if os.path.islink(args.saida):
                raise ValueError("Saída do relatório não pode ser symlink.")
            with open(args.saida, "w", encoding="utf-8") as arquivo:
                arquivo.write(texto)
            print(f"Relatório salvo em {os.path.abspath(args.saida)}")
        else:
            print(texto, end="")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")


if __name__ == "__main__":
    main()
