"""Apresentação e sessão guiada pelas três entregas, fora das medições."""

import os

from .heuristica import validar_alfa
from .metricas import metricas_principais
from .pastas import lembrar_pasta, menu_pastas, validar_pasta
from .relatorio import (carregar_resultados, criar_registro, gerar_relatorio_etapa,
                        salvar_markdown, salvar_registro)


ALGORITMOS_ETAPA = {1: ("BFS", "DFS"), 2: ("BFS", "DFS", "UCS", "A*"), 3: ("UCS", "A*")}


def apresentar_etapa(registros, etapa, alvo, args, *, resumido=False):
    """Salve a entrega completa e exiba o resumo quando solicitado pelo menu."""
    texto = gerar_relatorio_etapa(registros, etapa, alvo)
    arquivos = []
    if not args.sem_salvar:
        for registro in registros:
            caminho = salvar_registro(registro, args.resultados)
            registro["origem_json"] = caminho
            arquivos.append(caminho)
        markdown = salvar_markdown(texto, os.path.join(args.resultados, f"etapa_{etapa}.md"))
    print(gerar_relatorio_etapa(registros, etapa, alvo, resumido=True) if resumido else texto)
    if arquivos:
        print(f"{len(arquivos)} JSONs salvos em {os.path.abspath(args.resultados)}")
        print(f"Relatório completo salvo em {markdown}")
    return texto


def apresentar_busca(raiz, alvo, estrategia, modo, alfa, caminhos, metricas, args):
    """Apresente uma busca individual e retorne seu registro para gráficos opcionais."""
    registro = criar_registro(raiz, alvo, estrategia, modo, caminhos, metricas, alfa)
    print(f"\nBusca: {'A*' if estrategia == 'astar' else estrategia.upper()} | modo: {modo}")
    if estrategia == "astar":
        print(f"alfa: {alfa:g}; heurística não admissível, sem garantia de caminho ótimo.")
    print("\n".join(caminhos) if caminhos else "Nenhum arquivo encontrado.")
    for campo, valor in metricas_principais(metricas, modo).items():
        print(f"{campo}: {valor:.3f}" if isinstance(valor, float) else f"{campo}: {valor}")
    print(f"Arquivos encontrados: {metricas.arquivos_encontrados}")
    if not args.sem_salvar:
        print(f"JSON salvo em {salvar_registro(registro, args.resultados)}")
    return registro


def exportar_registros(registros, diretorio):
    """Importe o extra apenas sob solicitação; use os dados já medidos."""
    from .visualizacao import gerar_graficos
    for caminho in gerar_graficos(registros, diretorio):
        print(f"Gráfico salvo em {caminho}")


def exportar_arquivos(entradas, diretorio):
    """Converta JSONs existentes em gráficos, sem executar buscas."""
    from .visualizacao import verificar_dependencia
    verificar_dependencia()
    exportar_registros(carregar_resultados(entradas), diretorio)


def _opcao(pergunta, validas, padrao=""):
    while True:
        resposta = input(pergunta).strip().casefold() or padrao
        if resposta in validas:
            return resposta
        print("Opção inválida; use uma das alternativas exibidas.")


def _termo(modo, termos):
    pergunta = "Palavra no conteúdo" if modo == "conteudo" else "Palavra no nome"
    termos[modo] = input(f"{pergunta} [{termos[modo]}]: ").strip() or termos[modo]
    return termos[modo]


def _progresso(nomes):
    def informar(fase, indice, total):
        print(f"[{fase} {indice}/{total}] {nomes[indice - 1]}", flush=True)
    return informar


def _apos_execucao(args, registros=None, texto=None, etapa=None):
    """Retorne próxima etapa, None para menu ou zero para encerrar, sem recursão."""
    validas = {"s", "sim", "m", "n", "nao", "não", "0"}
    extras = []
    if registros:
        validas.add("g")
        extras.append("g: gráfico (requer Matplotlib)")
    if texto is not None:
        validas.add("r")
        extras.append("r: relatório completo")
    if etapa in (1, 2):
        validas.add("p")
        extras.insert(0, f"p: seguir para a etapa {etapa + 1}")
    while True:
        if extras:
            print(" | ".join(extras))
        pergunta = "Deseja voltar ao menu? [S/n]"
        resposta = _opcao(pergunta + (" (ou escolha uma ação acima): " if extras else ": "), validas, "s")
        if resposta in ("s", "sim", "m"):
            return None
        if resposta in ("n", "nao", "não", "0"):
            return 0
        if resposta == "p":
            return etapa + 1
        if resposta == "r":
            print(texto)
        elif resposta == "g":
            try:
                exportar_registros(registros, os.path.join(args.resultados, "graficos"))
            except (OSError, ValueError, RuntimeError) as erro:
                print(f"Não foi possível gerar o gráfico: {erro}")


def executar_menu(args, raiz, sugestao, executar_etapa, executar):
    """Mantenha pasta, termos e alfa na sessão; receba as APIs sem importar main."""
    termos = {"nome": args.alvo or sugestao or "livro", "conteudo": args.alvo or "algoritmo"}
    alfa = args.alfa if args.alfa is not None else 1.0
    pendente = None
    recomendada = 1
    while True:
        if pendente is None:
            print(f"\nFile Hunter Agent — Comparações\nPasta atual: {os.path.abspath(raiz)}")
            print("1. Etapa 1 — Mapear arquivos (BFS × DFS)"
                  "\n2. Etapa 2 — Comparar busca por nome (BFS, DFS, UCS e A*)"
                  "\n3. Etapa 3 — Comparar conteúdo (UCS × A*)"
                  "\n4. Escolher outra pasta\n5. Mais opções\n0. Sair")
            opcao = _opcao(f"Etapa ou opção [{recomendada}]: ", {"0", "1", "2", "3", "4", "5"}, str(recomendada))
            if opcao == "0":
                return
        else:
            opcao = str(pendente)
            pendente = None
        try:
            if opcao == "4":
                escolha = menu_pastas(raiz)
                if escolha is not None:
                    raiz, sugestao = escolha
                    raiz = lembrar_pasta(raiz, args.config)
                    if sugestao and args.alvo is None:
                        termos["nome"] = sugestao
                continue
            if opcao == "5":
                print("\n1. Busca individual\n2. Gráficos de JSONs salvos (opcional; requer Matplotlib)"
                      f"\n3. Ajustar heurística A* (alfa atual: {alfa:g})\n0. Voltar")
                extra = _opcao("Mais opções: ", {"0", "1", "2", "3"})
                if extra == "0":
                    continue
                if extra == "2":
                    from .visualizacao import verificar_dependencia
                    verificar_dependencia()
                    entrada = input(f"Arquivo JSON ou pasta de resultados [{args.resultados}]: ").strip() or args.resultados
                    exportar_arquivos([entrada], os.path.join(args.resultados, "graficos"))
                    if _apos_execucao(args) == 0:
                        return
                    continue
                if extra == "3":
                    valor = input(f"Peso alfa, finito e não negativo [{alfa:g}]: ").strip()
                    alfa = validar_alfa(float(valor) if valor else alfa)
                    print(f"alfa={alfa:g}. A heurística não garante caminho ótimo ou economia.")
                    continue
                print("\n1. BFS\n2. DFS\n3. UCS\n4. A*\n0. Voltar")
                algoritmo = _opcao("Algoritmo: ", {"0", "1", "2", "3", "4"})
                if algoritmo == "0":
                    continue
                estrategia = {"1": "bfs", "2": "dfs", "3": "ucs", "4": "astar"}[algoritmo]
                modo = args.modo
                if modo is None:
                    modo = "conteudo" if _opcao("1. Nome  2. Conteúdo [1]: ", {"1", "2"}, "1") == "2" else "nome"
                alvo = _termo(modo, termos)
                caminhos, metricas = executar(raiz, alvo, estrategia, modo, alfa,
                                              progresso=_progresso(["A*" if estrategia == "astar" else estrategia.upper()]))
                registro = apresentar_busca(raiz, alvo, estrategia, modo, alfa, caminhos, metricas, args)
                if _apos_execucao(args, [registro]) == 0:
                    return
                continue
            etapa = int(opcao)
            try:
                validar_pasta(raiz)
            except (OSError, ValueError) as erro:
                print(f"Escolha a pasta do acervo para continuar: {erro}")
                escolha = menu_pastas(raiz)
                if escolha is None:
                    continue
                raiz, sugestao = escolha
                raiz = lembrar_pasta(raiz, args.config)
                if sugestao and args.alvo is None:
                    termos["nome"] = sugestao
            alvo = None if etapa == 1 else _termo("nome" if etapa == 2 else "conteudo", termos)
            nomes = ALGORITMOS_ETAPA[etapa]
            print(f"\nEtapa {etapa} — Comparando {' × '.join(nomes)}")
            registros = executar_etapa(etapa, raiz, alvo, alfa, progresso=_progresso(nomes))
            texto = apresentar_etapa(registros, etapa, alvo, args, resumido=True)
            print(f"\nEtapa {etapa} concluída.")
            recomendada = etapa + 1 if etapa < 3 else 1
            pendente = _apos_execucao(args, registros, texto, etapa)
            if pendente == 0:
                return
        except (OSError, ValueError, RuntimeError) as erro:
            print(f"Não foi possível concluir a operação: {erro}")
            if _apos_execucao(args) == 0:
                return
