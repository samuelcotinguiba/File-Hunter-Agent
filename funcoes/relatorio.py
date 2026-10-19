"""Persistência de execuções e conversão de JSON em tabelas Markdown."""

import argparse
import json
import os
import time

from .metricas import (Metricas, PROTOCOLO_LOTE, ROTULOS_PRINCIPAIS,
                       metricas_principais, metodologia_medicao)
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
    escopo = parametros.get("escopo", "objetivo")
    if escopo not in ("objetivo", "mapeamento"):
        raise ValueError("Escopo deve ser objetivo ou mapeamento.")
    for campo in (("raiz",) if escopo == "mapeamento" else ("raiz", "alvo")):
        if not isinstance(parametros.get(campo), str) or not parametros[campo]:
            raise ValueError(f"Parâmetro {campo} ausente ou inválido.")
    if parametros.get("algoritmo") not in ("bfs", "dfs", "ucs", "astar"):
        raise ValueError("Algoritmo inválido no registro.")
    if parametros.get("modo") not in ("nome", "conteudo"):
        raise ValueError("Modo inválido no registro.")
    etapa = parametros.get("etapa")
    if etapa is not None and (type(etapa) is not int or etapa not in (1, 2, 3)):
        raise ValueError("Etapa deve ser 1, 2 ou 3.")
    if escopo == "mapeamento":
        if (etapa != 1 or parametros.get("alvo") is not None
                or parametros["algoritmo"] not in ("bfs", "dfs") or parametros["modo"] != "nome"):
            raise ValueError("Mapeamento é exclusivo de BFS/DFS na etapa 1, sem alvo ou conteúdo.")
    elif etapa == 1:
        raise ValueError("Etapa 1 exige escopo mapeamento.")
    if etapa == 2 and parametros["modo"] != "nome":
        raise ValueError("Etapa 2 exige busca por nome.")
    if etapa == 3 and (parametros["modo"] != "conteudo" or parametros["algoritmo"] not in ("ucs", "astar")):
        raise ValueError("Etapa 3 compara UCS/A* por conteúdo.")
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
    if escopo == "mapeamento" and (metricas["custo_g"] != 0 or metricas["arquivos_encontrados"] != len(encontrados)):
        raise ValueError("Mapeamento não tem g objetivo e deve conter todos os arquivos contados.")
    if "primeiros_10" in registro and registro["primeiros_10"] != encontrados[:10]:
        raise ValueError("primeiros_10 deve preservar a ordem de descoberta.")
    if "base_caminhos" in registro and (not isinstance(registro["base_caminhos"], str)
                                         or not os.path.isabs(registro["base_caminhos"])):
        raise ValueError("base_caminhos deve ser absoluta.")
    if "experimento" in registro and (not isinstance(registro["experimento"], str) or not registro["experimento"]):
        raise ValueError("Identificação do experimento deve ser texto não vazio.")
    if "expansoes" in registro:
        expansoes = registro["expansoes"]
        if not isinstance(expansoes, list) or len(expansoes) != metricas["pastas_abertas"]:
            raise ValueError("Rastro de expansões deve corresponder a N.")
        custos = {}
        raiz = os.path.normpath(parametros["raiz"])
        for expansao in expansoes:
            if (not isinstance(expansao, dict) or not isinstance(expansao.get("diretorio"), str)
                    or not os.path.isabs(expansao["diretorio"])
                    or any(type(expansao.get(c)) is not int or expansao[c] < 0 for c in ("custo_local", "g"))):
                raise ValueError("Expansão exige diretório absoluto, custo local e g não negativos.")
            pasta = os.path.normpath(expansao["diretorio"])
            pai = os.path.dirname(pasta)
            if pasta in custos or (pasta != raiz and pai not in custos):
                raise ValueError("Rastro contém repetição ou filho anterior ao pai.")
            esperado = expansao["custo_local"] + (custos[pai] if pasta != raiz else 0)
            if expansao["g"] != esperado:
                raise ValueError("g no rastro deve somar custo do pai e custo local.")
            custos[pasta] = esperado
        if encontrados and escopo == "objetivo":
            pasta_objetivo = os.path.normpath(os.path.dirname(encontrados[0]))
            if custos.get(pasta_objetivo) != metricas["custo_g"]:
                raise ValueError("g final difere do custo registrado no caminho objetivo.")
    if "medicao" in registro and registro["medicao"] != metodologia_medicao():
        raise ValueError("Medição deve usar perf_counter e pico tracemalloc em execuções separadas.")
    if "protocolo_lote" in registro and registro["protocolo_lote"] != PROTOCOLO_LOTE:
        raise ValueError("Protocolo do lote deve medir tempos antes dos perfis de memória.")
    avaliacao = registro.get("avaliacao_final")
    if avaliacao is not None:
        if (not encontrados or parametros["algoritmo"] not in ("ucs", "astar")
                or not isinstance(avaliacao, dict)
                or any(type(avaliacao.get(c)) is not int for c in ("g", "h", "f"))
                or avaliacao != {"g": metricas["custo_g"], "h": 0, "f": metricas["custo_g"]}):
            raise ValueError("Avaliação final deve satisfazer h=0 e f=g no objetivo UCS/A*.")
    return registro


def criar_registro(raiz, alvo, algoritmo, modo, encontrados, metricas, alfa=1.0,
                   *, etapa=None, visitas=None):
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
            "escopo": "mapeamento" if etapa == 1 else "objetivo",
            "etapa": etapa,
        },
        "encontrados": list(encontrados),
        "metricas": vars(metricas).copy(),
        "medicao": metodologia_medicao(),
        "base_caminhos": os.getcwd(),
        "avaliacao_final": ({"g": metricas.custo_g, "h": 0, "f": metricas.custo_g}
                            if encontrados and algoritmo in ("ucs", "astar") else None),
    }
    if visitas is not None:
        registro["expansoes"] = [dict(v) for v in visitas]
    if etapa == 1:
        registro["primeiros_10"] = list(encontrados[:10])
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
    protocolos = set()
    for indice, registro in enumerate(registros, 1):
        validar_registro(registro)
        protocolos.add(registro.get("protocolo_lote"))
        p, m = registro["parametros"], registro["metricas"]
        principais = metricas_principais(m, p["modo"])
        if p.get("escopo") == "mapeamento":
            principais["Custo do Caminho g(n)"] = "Não se aplica (mapeamento)"
        valores = [f"{v:.3f}" if isinstance(v, float) else v for v in principais.values()]
        campos = [indice, "A*" if p["algoritmo"] == "astar" else p["algoritmo"].upper(),
                  len(registro["encontrados"]), m["arquivos_encontrados"]] + valores
        linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
    linhas.extend([
        "", "N conta diretórios abertos; itens examinados inclui arquivos e subpastas da listagem.",
        "Arquivos processados/lidos conta conteúdos efetivamente lidos por execução.",
        "Memória: pico de alocações Python via tracemalloc (KiB), não RSS do processo.",
        "Tempo: diferença de time.perf_counter em ms, sem tracemalloc ativo.",
        "Tempo e memória usam execuções separadas; contadores não são somados entre elas.",
        "O cronômetro inclui a busca inteira, E/S, heurística e rastro; exclui menu, impressão e gravação de resultados.",
        "Tempo decorrido não é tempo de CPU nem tempo exclusivo de disco; cache e carga do sistema influenciam a amostra.",
        "No mapeamento global não existe um caminho objetivo único para g(n).", "",
    ])
    if protocolos == {PROTOCOLO_LOTE}:
        linhas.extend(["Protocolo do lote: todos os tempos primeiro, depois todos os perfis de memória.",
                       "Uma amostra por algoritmo, em ordem fixa; não há limpeza do cache do sistema.", ""])
    return "\n".join(linhas)


def caminho_relativo(registro, caminho):
    """Apresente o caminho completo relativo à base registrada, sem acessar disco."""
    base = registro.get("base_caminhos", os.getcwd())
    return "./" + os.path.relpath(caminho, base).replace(os.path.sep, "/")


def _tabela(cabecalho, linhas):
    resultado = ["| " + " | ".join(cabecalho) + " |",
                 "| " + " | ".join("---" for _ in cabecalho) + " |"]
    resultado.extend("| " + " | ".join(_celula(c) for c in linha) + " |" for linha in linhas)
    return "\n".join(resultado)


def _percursos(registros):
    """Mostre a ordem real das expansões, não somente o caminho da solução."""
    linhas = ["### Percurso de expansão dos diretórios", ""]
    for r in registros:
        algoritmo = "A*" if r["parametros"]["algoritmo"] == "astar" else r["parametros"]["algoritmo"].upper()
        linhas.extend([f"{algoritmo}:", ""])
        visitas = r.get("expansoes")
        if visitas is None:
            linhas.extend(["Rastro não registrado neste JSON antigo.", ""])
        else:
            linhas.extend([_tabela(("Ordem", "Diretório expandido", "Custo local", "g do diretório"),
                                  ((i, caminho_relativo(r, v["diretorio"]), v["custo_local"], v["g"])
                                   for i, v in enumerate(visitas, 1))), ""])
    return "\n".join(linhas)


def _demonstrar_reducao(registros):
    pares = {alg: [r for r in registros if r["parametros"]["algoritmo"] == alg] for alg in ("ucs", "astar")}
    if any(len(pares[alg]) != 1 for alg in pares):
        return "### Redução de expansões/leituras\n\nSelecione exatamente um UCS e um A* do mesmo experimento.\n"
    ucs, astar = pares["ucs"][0], pares["astar"][0]
    linhas = ["### Redução de expansões/leituras", "",
              _tabela(("Métrica", "UCS", "A*", "Diferença UCS − A*"),
                      ((rotulo, ucs["metricas"][campo], astar["metricas"][campo],
                        ucs["metricas"][campo] - astar["metricas"][campo])
                       for campo, rotulo in (("pastas_abertas", "Nós expandidos (N)"),
                                              ("arquivos_lidos", "Arquivos efetivamente lidos")))), "",
              "Diferença positiva indica redução; negativa indica trabalho adicional de A*.",
              "A heurística muda a ordem. A parada no objetivo pode deixar pastas sem expansão;",
              "não elimina permanentemente pastas nem garante custo ótimo ou economia.", ""]
    if "expansoes" in ucs and "expansoes" in astar:
        visitadas_a = {os.path.normpath(v["diretorio"]) for v in astar["expansoes"]}
        evitadas = [v for v in ucs["expansoes"] if os.path.normpath(v["diretorio"]) not in visitadas_a]
        linhas.extend(["Diretórios expandidos por UCS e não expandidos por A* neste experimento:", ""])
        linhas.extend(["- " + _celula(caminho_relativo(ucs, v["diretorio"])) for v in evitadas]
                      or ["Nenhum."])
        linhas.append("")
    return "\n".join(linhas)


def gerar_relatorio_etapa(registros, etapa, alvo=None, *, resumido=False):
    """Entregas separadas: global BFS/DFS, nome com quatro buscas e conteúdo UCS/A*."""
    if type(etapa) is not int or etapa not in (1, 2, 3):
        raise ValueError("Etapa deve ser 1, 2 ou 3.")
    if etapa == 1 and alvo is not None:
        raise ValueError("Mapeamento não recebe alvo.")
    termo = alvo if alvo is not None else ("livro" if etapa == 2 else "algoritmo")
    grupos = {}
    for r in registros:
        validar_registro(r)
        p = r["parametros"]
        if etapa == 1:
            selecionado = p.get("escopo") == "mapeamento"
        else:
            selecionado = (p.get("escopo", "objetivo") == "objetivo"
                            and p["modo"] == ("nome" if etapa == 2 else "conteudo")
                            and p["alvo"].casefold() == termo.casefold())
        permitidos = ("bfs", "dfs", "ucs", "astar") if etapa == 2 else (("bfs", "dfs") if etapa == 1 else ("ucs", "astar"))
        if selecionado and p["algoritmo"] in permitidos:
            chave = (p["raiz"], r.get("experimento"),
                     tuple(sorted(p.get("extensoes_texto") or [])), p.get("extrator_pdf"),
                     r.get("protocolo_lote"))
            grupos.setdefault(chave, []).append(r)
    if not grupos:
        raise ValueError(f"Não há registros correspondentes à etapa {etapa}.")
    titulos = {1: "Mapeamento global BFS × DFS", 2: "Busca por palavra no nome", 3: "Busca por conteúdo UCS × A*"}
    linhas = [f"# Etapa {etapa} — {titulos[etapa]}", ""]
    for (raiz, experimento, _, _, protocolo), grupo in grupos.items():
        ordem = {a: i for i, a in enumerate(("bfs", "dfs", "ucs", "astar"))}
        grupo.sort(key=lambda r: ordem[r["parametros"]["algoritmo"]])
        linhas.extend(["Raiz: " + _celula(raiz), "",
                       "Experimento: " + _celula(experimento or "não registrado"), "",
                       "Protocolo do lote: " + _celula(protocolo or "não registrado"), ""])
        if etapa == 1:
            pares = {}
            for r in grupo:
                algoritmo = r["parametros"]["algoritmo"]
                if algoritmo in pares:
                    raise ValueError(f"Mais de uma execução {algoritmo.upper()} no mesmo grupo; "
                                     "selecione um JSON por algoritmo e experimento.")
                pares[algoritmo] = r
            linhas.extend([
                "Somente BFS e DFS percorrem a árvore inteira nesta etapa, sem ler conteúdos.",
                "KB nas tabelas da entrega usa 1000 bytes; as métricas principais usam KiB (1024 bytes).", "",
                _tabela(("Algoritmo", "Total de Pastas Abertas", "Total de Arquivos Encontrados", "Tempo (ms)", "Pico de Memória (KB)"),
                        ((r["parametros"]["algoritmo"].upper(), r["metricas"]["pastas_abertas"],
                          r["metricas"]["arquivos_encontrados"], f'{r["metricas"]["tempo_ms"]:.3f}',
                          f'{r["metricas"]["pico_mem_kb"] * 1024 / 1000:.3f}') for r in grupo)), "",
                "### Ordem de descoberta — primeiros 10 arquivos", "",
            ])
            maximo = min(10, max(len(r["encontrados"]) for r in grupo))
            linhas.append(_tabela(("Ordem de Descoberta", "BFS — Caminho Completo", "DFS — Caminho Completo"),
                                  ((i + 1,) + tuple(caminho_relativo(pares[a], pares[a]["encontrados"][i])
                                                    if a in pares and i < len(pares[a]["encontrados"]) else "—"
                                                    for a in ("bfs", "dfs")) for i in range(maximo))))
            if set(pares) != {"bfs", "dfs"}:
                linhas.extend(["", "Comparação incompleta: falta BFS ou DFS."])
            if not resumido:
                linhas.extend(["", "### Todos os arquivos na ordem de descoberta", "",
                               _tabela(("Algoritmo", "Ordem de Descoberta", "Caminho Completo"),
                                       ((r["parametros"]["algoritmo"].upper(), i, caminho_relativo(r, c))
                                        for r in grupo for i, c in enumerate(r["encontrados"], 1))), ""])
        elif etapa == 2:
            linhas.extend([
                "Custo local = arquivos + subpastas. g soma os custos da raiz até a pasta do alvo.",
                "O tamanho da pasta só é conhecido ao expandi-la: o heap usa avaliação adiada,",
                "sem listagens antecipadas gratuitas. Menor g não significa menor custo local isolado.",
                "Memória (KB) usa 1000 bytes; o pico padrão em KiB permanece na tabela complementar.", "",
                _tabela(("Algoritmo", "Alvo Solicitado", "Caminho", "Pastas Abertas", "Custo Acumulado g(n)", "Tempo (ms)", "Memória (KB)"),
                        (("A*" if r["parametros"]["algoritmo"] == "astar" else r["parametros"]["algoritmo"].upper(),
                          r["parametros"]["alvo"], caminho_relativo(r, r["encontrados"][0]) if r["encontrados"] else "Não encontrado",
                          r["metricas"]["pastas_abertas"], f'{r["metricas"]["custo_g"]} itens' if r["encontrados"] else "—",
                          f'{r["metricas"]["tempo_ms"]:.3f}', f'{r["metricas"]["pico_mem_kb"] * 1024 / 1000:.3f}') for r in grupo)), "",
                "### Análise do custo acumulado no caminho objetivo", "",
            ])
            analise = []
            for r in grupo:
                if not r["encontrados"]:
                    continue
                indice = {os.path.normpath(v["diretorio"]): v for v in r.get("expansoes", [])}
                pasta = os.path.normpath(os.path.dirname(r["encontrados"][0]))
                caminho = []
                while pasta in indice:
                    caminho.append(indice[pasta])
                    pai = os.path.dirname(pasta)
                    if pai == pasta:
                        break
                    pasta = pai
                analise.extend(("A*" if r["parametros"]["algoritmo"] == "astar" else r["parametros"]["algoritmo"].upper(), caminho_relativo(r, v["diretorio"]),
                                v["custo_local"], v["g"]) for v in reversed(caminho))
            linhas.extend([_tabela(("Algoritmo", "Diretório do caminho", "Custo local (itens)", "g acumulado"), analise), ""])
            if not analise:
                linhas.extend(["Sem rastro de custo disponível ou sem objetivo encontrado.", ""])
            if {r["parametros"]["algoritmo"] for r in grupo} != {"bfs", "dfs", "ucs", "astar"}:
                linhas.extend(["Comparação incompleta: faltam algoritmos da etapa 2.", ""])
            linhas.extend([gerar_metricas_principais(grupo), _demonstrar_reducao(grupo)])
        else:
            linhas.append(gerar_tabela_comparativa(grupo, termo))
        if etapa == 1:
            linhas.append(gerar_metricas_principais(grupo))
        if not resumido:
            linhas.append(_percursos(grupo))
    return "\n".join(linhas)


def salvar_markdown(texto, caminho):
    """Grave o relatório solicitado, preservando a validação de destino."""
    caminho = os.path.abspath(caminho)
    if not caminho.lower().endswith(".md"):
        raise ValueError("O arquivo de saída deve ter extensão .md.")
    if os.path.islink(caminho):
        raise ValueError("Saída do relatório não pode ser symlink.")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
    return caminho


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
        chave = (os.path.realpath(p["raiz"]), politica, p.get("extrator_pdf", "não registrado"),
                 registro.get("experimento"), registro.get("protocolo_lote"))
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
        "h(n)=alfa*(1-J(B(nome_pasta), B(termo))), com Jaccard de bigramas após casefold.",
        "Pastas pendentes usam g do pai + h; a expansão revela o custo local. Objetivos usam h=0.", "",
    ]
    for (raiz, extensoes, extrator_pdf, experimento, protocolo), grupo in grupos.items():
        linhas.extend([
            f"Raiz: {_celula(raiz)}", "",
            "Extensões de texto: " + _celula(", ".join(extensoes) if extensoes is not None else "não registrado"), "",
            "Extrator PDF: " + _celula(extrator_pdf), "",
            "Experimento: " + _celula(experimento or "não registrado"), "",
            "Protocolo do lote: " + _celula(protocolo or "não registrado"), "",
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
                "\n".join(caminho_relativo(registro, c) for c in caminhos) if caminhos else "Não encontrado",
                m["pastas_abertas"], m["arquivos_lidos"],
                f'{m["custo_g"]} bytes' if caminhos else "—",
                f'{m["tempo_ms"]:.3f}',
            )
            linhas.append("| " + " | ".join(_celula(c) for c in campos) + " |")
        linhas.append("")
        linhas.append(gerar_metricas_principais(ordenados))
        linhas.append(_demonstrar_reducao(ordenados))
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
                  p["modo"], p["raiz"], "Sem alvo (mapeamento)" if p.get("escopo") == "mapeamento" else p["alvo"],
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
    parser.add_argument("--etapa", type=int, choices=(1, 2, 3), help="Relatório específico de uma etapa")
    parser.add_argument("--alvo", help="Termo do relatório (padrão: livro na etapa 2; algoritmo na etapa 3)")
    args = parser.parse_args()
    try:
        registros = carregar_resultados(args.entradas)
        if args.etapa is not None and args.comparativo:
            parser.error("Selecione --etapa ou --comparativo.")
        if args.etapa is not None:
            texto = gerar_relatorio_etapa(registros, args.etapa, args.alvo)
        elif args.comparativo:
            texto = gerar_tabela_comparativa(registros, args.alvo or "algoritmo")
        else:
            texto = gerar_markdown(registros)
        if args.saida:
            print(f"Relatório salvo em {salvar_markdown(texto, args.saida)}")
        else:
            print(texto, end="")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")


if __name__ == "__main__":
    main()
