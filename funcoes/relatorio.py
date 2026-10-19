"""Persistência de execuções e conversão de JSON em tabelas Markdown."""

import argparse
import json
import os
import time

from .metricas import Metricas, ROTULOS_PRINCIPAIS, metricas_principais, metodologia_medicao
from .conteudo import EXTENSOES_TEXTO
from .pdf import EXTRATOR_PDF


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
    extensoes = parametros.get("extensoes_texto")
    if extensoes is not None:
        if (not isinstance(extensoes, list)
                or any(not isinstance(e, str) or not e.startswith(".") or len(e) < 2 for e in extensoes)):
            raise ValueError("extensoes_texto deve ser uma lista de extensões.")
    if "extrator_pdf" in parametros and parametros["extrator_pdf"] is not None and not isinstance(parametros["extrator_pdf"], str):
        raise ValueError("extrator_pdf deve identificar o extrator ou ser null.")
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
    if "medicao" in registro and registro["medicao"] != metodologia_medicao():
        raise ValueError("Medição deve usar perf_counter e pico tracemalloc em execuções separadas.")
    avaliacao = registro.get("avaliacao_final")
    if avaliacao is not None:
        if (not encontrados or parametros["algoritmo"] not in ("ucs", "astar")
                or not isinstance(avaliacao, dict)
                or any(type(avaliacao.get(c)) is not int for c in ("g", "h", "f"))
                or avaliacao != {"g": metricas["custo_g"], "h": 0, "f": metricas["custo_g"]}):
            raise ValueError("Avaliação final deve satisfazer h=0 e f=g no objetivo UCS/A*.")
    return registro


def criar_registro(raiz, alvo, algoritmo, modo, encontrados, metricas, alfa=1.0):
    """Monte e valide o registro sem gravar, preservando uso isolado dos dados."""
    registro = {
        "versao": 1,
        "instante_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parametros": {
            "raiz": os.path.realpath(raiz), "alvo": alvo,
            "algoritmo": algoritmo, "modo": modo,
            "alfa": alfa if algoritmo == "astar" else None,
            "extensoes_texto": sorted(EXTENSOES_TEXTO) if modo == "conteudo" else None,
            "extrator_pdf": EXTRATOR_PDF if modo == "conteudo" else None,
        },
        "encontrados": list(encontrados),
        "metricas": vars(metricas).copy(),
        "medicao": metodologia_medicao(),
        "avaliacao_final": ({"g": metricas.custo_g, "h": 0, "f": metricas.custo_g}
                            if encontrados and algoritmo in ("ucs", "astar") else None),
    }
    validar_registro(registro)
    return registro


def salvar_execucao(raiz, alvo, algoritmo, modo, encontrados, metricas,
                    alfa=1.0, diretorio="resultados"):
    """Salve um JSON exclusivo após as medições; retorne seu caminho absoluto."""
    registro = criar_registro(raiz, alvo, algoritmo, modo, encontrados, metricas, alfa)
    return salvar_registro(registro, diretorio)


def salvar_registro(registro, diretorio="resultados"):
    """Grave registro validado sem sobrescrever execuções anteriores."""
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


def gerar_metricas_principais(registros, titulo="### Métricas principais"):
    """Tabela única de padrões obrigatórios para relatório geral e comparação."""
    cabecalho = ("ID", "Algoritmo", "Retornados", "Encontrados") + ROTULOS_PRINCIPAIS
    linhas = [titulo, "", "| " + " | ".join(cabecalho) + " |",
              "| " + " | ".join("---" for _ in cabecalho) + " |"]
    for indice, registro in enumerate(registros, 1):
        validar_registro(registro)
        p, m = registro["parametros"], registro["metricas"]
        principais = metricas_principais(m, p["modo"])
        valores = [f"{v:.3f}" if isinstance(v, float) else v for v in principais.values()]
        campos = [indice, "A*" if p["algoritmo"] == "astar" else p["algoritmo"].upper(),
                  len(registro["encontrados"]), m["arquivos_encontrados"]] + valores
        linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
    linhas.extend([
        "", "N conta diretórios abertos; itens examinados inclui arquivos e subpastas da listagem.",
        "Arquivos processados/lidos conta conteúdos efetivamente lidos por execução.",
        "Memória: pico de alocações Python via tracemalloc (KiB), não RSS do processo.",
        "Tempo: diferença de time.perf_counter em ms, sem tracemalloc ativo.",
        "Tempo e memória usam execuções separadas; contadores não são somados entre elas.", "",
    ])
    return "\n".join(linhas)


def gerar_tabela_comparativa(registros, alvo="algoritmo"):
    """Compare UCS e A* por conteúdo com as sete colunas da etapa 3.

    O custo f corresponde à candidatura objetivo confirmada: h=0 e f=g.
    Sem objetivo, f não é definido. Agrupe políticas de texto e raízes distintas
    para não apresentar experiências diferentes como uma única comparação.
    """
    grupos = {}
    for registro in registros:
        validar_registro(registro)
        p = registro["parametros"]
        if (p["algoritmo"] not in ("ucs", "astar") or p["modo"] != "conteudo"
                or p["alvo"].casefold() != alvo.casefold()):
            continue
        extensoes = p.get("extensoes_texto")
        politica = tuple(sorted(extensoes)) if extensoes is not None else None
        chave = (os.path.realpath(p["raiz"]), politica, p.get("extrator_pdf", "não registrado"))
        grupos.setdefault(chave, []).append(registro)
    if not grupos:
        raise ValueError(f"Nenhuma execução UCS/A* por conteúdo para o termo {alvo!r}.")
    linhas = [
        "## Métricas comparativas — UCS e A*", "",
        "f(n)=g(n)+h(n); UCS usa h=0. No objetivo confirmado de A*, h=0 e f=g.",
        "O custo final usa bytes do caminho; não é a soma dos bytes de toda a exploração.",
        "Arquivos lidos conta aberturas para leitura pela aplicação, inclusive releituras",
        "por caminhos distintos. Cache do sistema pode atender essas leituras sem acesso físico ao disco.",
        "Contadores são de uma execução; tempo e memória são medidos em chamadas separadas.", "",
    ]
    for (raiz, extensoes, extrator_pdf), grupo in grupos.items():
        linhas.extend([
            f"Raiz: {_celula(raiz)}", "",
            "Extensões de texto: " + _celula(", ".join(extensoes) if extensoes is not None else "não registrado"), "",
            "Extrator PDF: " + _celula(extrator_pdf), "",
        ])
        pesos = sorted({r["parametros"]["alfa"] for r in grupo if r["parametros"]["algoritmo"] == "astar"})
        if pesos:
            linhas.extend(["A*: alfa(s) " + ", ".join(str(p) for p in pesos) + ". Heurística não admissível.", ""])
        presentes = {r["parametros"]["algoritmo"] for r in grupo}
        if presentes != {"ucs", "astar"}:
            linhas.extend(["Comparação incompleta: falta uma execução UCS ou A* neste grupo.", ""])
        linhas.extend([
            "| Algoritmo | Palavra no Conteúdo | Caminho | Pastas Abertas | Arquivos Lidos do Disco | Custo Total f(n) | Tempo (ms) |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ])
        ordenados = sorted(grupo, key=lambda r: r["parametros"]["algoritmo"] != "ucs")
        for registro in ordenados:
            p, m = registro["parametros"], registro["metricas"]
            caminhos = registro["encontrados"]
            campos = (
                "UCS" if p["algoritmo"] == "ucs" else "A*", p["alvo"],
                "\n".join(caminhos) if caminhos else "Não encontrado",
                m["pastas_abertas"], m["arquivos_lidos"],
                f'{m["custo_g"]} bytes' if caminhos else "—",
                f'{m["tempo_ms"]:.3f}',
            )
            linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
        linhas.append("")
        linhas.append(gerar_metricas_principais(ordenados))
    return "\n".join(linhas)


def gerar_markdown(registros):
    """Gere tabelas de parâmetros e métricas sem executar novas buscas."""
    if not registros:
        raise ValueError("Nenhuma execução para relatar.")
    for registro in registros:
        validar_registro(registro)
    linhas = [
        "# Relatório File Hunter Agent", "",
        "Compare execuções com a mesma raiz, alvo, modo e extensões textuais. g usa itens no modo nome",
        "e bytes no modo conteúdo. Tempos e picos vêm de execuções separadas.", "",
        "## Parâmetros", "",
        "| ID | JSON | Algoritmo | Modo | Raiz | Alvo | Alfa | Extensões de texto | Extrator PDF |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for indice, registro in enumerate(registros, 1):
        p = registro["parametros"]
        extensoes = p.get("extensoes_texto")
        textos = (", ".join(extensoes) if extensoes is not None else "não registrado") if p["modo"] == "conteudo" else "—"
        campos = (indice, registro.get("origem_json", "—"), p["algoritmo"].upper(),
                  p["modo"], p["raiz"], p["alvo"],
                  p.get("alfa") if p["algoritmo"] == "astar" else "—", textos,
                  p.get("extrator_pdf", "não registrado") if p["modo"] == "conteudo" else "—")
        linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
    linhas.extend(["", gerar_metricas_principais(registros, "## Métricas principais")])
    linhas.extend([
        "", "Encontrados conta correspondências descobertas; retornados conta a pasta objetivo escolhida.",
        "Sem resultado, g é zero. Pastas e arquivos lidos contabilizam toda a exploração.",
        "A* usa heurística não admissível: não garante custo mínimo ou menor exploração.",
        "Pico mede alocações Python (KiB), não RSS. Cache do sistema e carga afetam o tempo.", "",
    ])
    if any(r["parametros"]["algoritmo"] in ("ucs", "astar")
           and r["parametros"]["modo"] == "conteudo"
           and r["parametros"]["alvo"].casefold() == "algoritmo" for r in registros):
        linhas.append(gerar_tabela_comparativa(registros))
    return "\n".join(linhas)


def main():
    """Converta JSONs com python3 -m funcoes.relatorio ENTRADAS --saida arquivo.md."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entradas", nargs="+", help="Arquivos JSON ou diretórios")
    parser.add_argument("--saida", help="Arquivo .md; omitido, imprime o relatório")
    parser.add_argument("--comparativo", action="store_true", help="Somente tabela UCS/A* por conteúdo")
    parser.add_argument("--alvo", default="algoritmo", help="Termo da tabela comparativa (padrão: algoritmo)")
    args = parser.parse_args()
    try:
        registros = carregar_resultados(args.entradas)
        texto = (gerar_tabela_comparativa(registros, args.alvo) if args.comparativo
                 else gerar_markdown(registros))
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
