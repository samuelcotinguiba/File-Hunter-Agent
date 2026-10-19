# File Hunter Agent

Projeto didático em Python 3 para comparar buscas em árvores de diretórios.
Estão implementados: estrutura, listagem segura, métricas, gerador de dados,
BFS, DFS e UCS por nome, menu e argumentos. A*, busca por conteúdo e relatórios
aguardam as próximas etapas.
Não há dependências externas. `dataclasses`, da biblioteca padrão, exige Python
3.7 ou posterior.

Execute a partir de `File-Hunter-Agent/`:

```sh
python3 gerar_arvore.py
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo bfs
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo dfs
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo ucs
python3 main.py
python3 -m tests.test_buscas
python3 -m tests.test_ucs
python3 -c 'from funcoes.listagem import listar_dir; print([e.name for e in listar_dir("docencia/fontes")])'
```

O gerador cria 40 pastas abaixo de `docencia/fontes/`, com profundidade máxima
de quatro níveis e 64 arquivos .txt, .md, .py e .png. A seed é 2024. Apenas parte
dos arquivos de texto contém `algoritmo`. A árvore gerada e os JSON de execuções
são ignorados pelo Git. Novas execuções sobrescrevem os arquivos conhecidos.

`listar_dir(caminho)` retorna `os.DirEntry` ordenados por nome, sem links
simbólicos. Erros de acesso são propagados. A listagem não atualiza contadores.
`Metricas` guarda contadores e custo; `medir_tempo` e `medir_memoria` retornam
`(resultado, medição)`. Execute cada auxiliar com estado novo e separado.

## Estruturas de dados e justificativas de design

- **Nó e expansão:** diretório; uma chamada de listagem representa uma expansão.
- **Listagem:** `os.scandir`, ordenação por nome e exclusão de symlinks.
- **Métricas:** dataclass com valores iniciais zero; tempo e memória separados.
- **BFS e DFS:** deque com popleft/pop; lógica de descoberta compartilhada.
  Param na primeira pasta com correspondências e retornam todos os alvos nela.
  Irmãos são expandidos em ordem alfabética. g soma as listagens do caminho até
  a pasta do resultado; sem resultado, g fica em zero. Não leem conteúdos.
- **UCS:** heap com prioridade, contador e nó. Pastas ainda não abertas usam o
  custo do pai como limite inferior; sua expansão calcula o custo exato e insere
  a candidatura a objetivo. A busca só encerra quando a candidatura sai do heap,
  garantindo custo mínimo em árvore estática sem listagem antecipada. Cada pasta
  é listada uma única vez por execução. O contador evita comparar nós em empates.
  arquivos_encontrados inclui correspondências de candidatos não selecionados.
- **A*:** a implementar, também com heap e contador de desempate.
- **Ciclos:** conjunto de realpaths marcados ao inserir na fronteira.
- **Custos e heurística:** definições registradas no AGENTS.md; heurística futura
  não admissível, sem garantia de caminho ótimo para A*.
- **Relatórios:** a implementar; JSON e tabelas Markdown.

## Progresso estimado

Percentuais representam funcionalidades entregues, não cobertura de testes ou
tempo restante. Cada linha tem o mesmo peso; escopo futuro ainda pode ser refinado.

| Entrega | Concluído |
| --- | ---: |
| Base do passo A | 100% |
| BFS e DFS por nome | 100% |
| UCS por nome (etapa 2) | 100% |
| Busca por conteúdo e custo em bytes (etapa 3) | 0% |
| Heurística e A* | 0% |
| Menu e CLI para todos os algoritmos | 75% |
| JSON e relatórios Markdown | 0% |
| **Total estimado (média simples)** | **54%** |

O percentual do menu acompanha os três algoritmos disponíveis dos quatro previstos
(BFS, DFS, UCS e A*). A integração do modo de conteúdo ainda está pendente.
