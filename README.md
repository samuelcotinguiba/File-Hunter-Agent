# File Hunter Agent

Projeto didático em Python 3 para comparar buscas em árvores de diretórios.
Estão implementados: estrutura, listagem segura, métricas, gerador de dados,
BFS, DFS e UCS por nome ou conteúdo, menu e argumentos. A* e relatórios
aguardam as próximas etapas.
Não há dependências externas. `dataclasses`, da biblioteca padrão, exige Python
3.7 ou posterior.

Execute a partir de `File-Hunter-Agent/`:

```sh
python3 gerar_arvore.py
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo bfs
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo dfs
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo ucs
python3 main.py --raiz ./docencia/fontes --alvo algoritmo --algoritmo ucs --modo conteudo
python3 main.py
python3 -m tests.test_buscas
python3 -m tests.test_ucs
python3 -m tests.test_conteudo
python3 -m tests
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

`--modo nome` é o padrão na CLI. No menu, escolha algoritmo e modo, depois informe
o termo. A busca por conteúdo considera `.txt`, `.md` e `.py` (inclusive extensões
em maiúsculas), usa UTF-8 com `errors="ignore"` e não diferencia maiúsculas no
termo. PNG e extensões desconhecidas não são lidos. A classificação é por extensão.
São lidos todos os textos de cada pasta expandida; g soma os bytes reais dessas
leituras no caminho da raiz até a pasta objetivo, incluindo ambas. O tamanho em
bytes é obtido do deslocamento binário ao terminar a leitura, preservando a
contagem de acentos, sequências inválidas e CRLF.
O contador `arquivos_lidos` abrange toda a exploração, inclusive ramos fora do
caminho final. Cada arquivo é lido até o fim, em blocos de 64 Ki caracteres, uma
vez por execução. A memória da leitura é O(tamanho do bloco + tamanho do termo),
sem cache entre as duas execuções de medição.

## Estruturas de dados e justificativas de design

- **Nó e expansão:** diretório; uma chamada de listagem representa uma expansão.
- **Listagem:** `os.scandir`, ordenação por nome e exclusão de symlinks.
- **Métricas:** dataclass com valores iniciais zero; tempo e memória separados.
- **BFS e DFS:** deque com popleft/pop; lógica de descoberta compartilhada.
  Param na primeira pasta com correspondências e retornam todos os alvos nela.
  Irmãos são expandidos em ordem alfabética. g soma as listagens do caminho até
  a pasta do resultado no modo nome, ou os bytes lidos no modo conteudo; sem
  resultado, g fica em zero. Somente o modo conteudo abre arquivos de texto.
- **UCS:** heap com prioridade, contador e nó. Pastas ainda não abertas usam o
  custo do pai como limite inferior; sua expansão calcula o custo exato e insere
  a candidatura a objetivo. A busca só encerra quando a candidatura sai do heap,
  garantindo custo mínimo em árvore estática sem listagem antecipada. Cada pasta
  é listada uma única vez por execução. O contador evita comparar nós em empates.
  arquivos_encontrados inclui correspondências de candidatos não selecionados.
- **A*:** a implementar, também com heap e contador de desempate.
- **Leitura compartilhada:** `examinar_arquivos` aplica o mesmo critério de texto,
  correspondência e custo para BFS, DFS e UCS. Não duplica leituras para medir bytes.
  `ler_texto` usa a decodificação incremental do próprio `open` e mantém a cauda
  após casefold para termos entre blocos. Mesmo um alvo encontrado no começo não
  interrompe a leitura, pois o custo inclui todos os bytes do arquivo.
- **Ciclos:** conjunto de realpaths marcados ao inserir na fronteira.
- **Custos e heurística:** definições registradas no AGENTS.md; heurística futura
  não admissível, sem garantia de caminho ótimo para A*.
- **Relatórios:** a implementar; JSON e tabelas Markdown.

### Decisões confirmadas na revisão

- **Responsabilidades separadas:** `main.py` coordena interface e medições; as
  buscas escolhem a fronteira; listagem e conteúdo concentram acesso ao disco.
  Isso permite testar cada política com custos conhecidos e reutilizar a leitura.
- **Percurso iterativo:** deque/heap evitam depender da profundidade de recursão.
  Visitados guardam apenas realpaths; não é preciso construir uma árvore de nós
  persistente ou adaptar classes de BST.
- **Menos alocações e trabalho descartado:** listagem ordena no próprio lugar;
  BFS/DFS não calculam realpaths dos filhos após encontrar a pasta objetivo.
- **Medições comparáveis:** cada busca cria seu próprio estado em cada chamada.
  Comparar resultados e contadores detecta divergências observáveis entre chamadas,
  mas não constitui uma fotografia imutável do sistema de arquivos. O pico medido
  é de alocações Python, não da memória total do processo nem do cache do sistema.
- **Verificação independente:** testes confrontam UCS com enumeração dos custos
  objetivos e leitura em blocos com uma referência integral. Na revisão, um arquivo
  de 4 MiB teve pico de 12.288,5 KiB com leitura integral e 325,3 KiB em blocos;
  os números variam por ambiente. Execute `python3 -m tests` sem `-O`.
- **Limites explícitos:** a árvore deve permanecer estável durante as buscas.
  A validação rejeita links inclusive antes de `..`, mas não impede alterações
  concorrentes entre verificação e abertura. Texto é classificado por extensão.

A justificativa final será consolidada após A* e relatórios, mantendo estes
critérios e registrando os compromissos das próximas implementações.

## Progresso estimado

Percentuais representam funcionalidades entregues, não cobertura de testes ou
tempo restante. Cada linha tem o mesmo peso; escopo futuro ainda pode ser refinado.

| Entrega | Concluído |
| --- | ---: |
| Base do passo A | 100% |
| BFS e DFS por nome | 100% |
| UCS por nome (etapa 2) | 100% |
| Busca por conteúdo e custo em bytes (etapa 3) | 100% |
| Heurística e A* | 0% |
| Menu e CLI para todos os algoritmos | 75% |
| JSON e relatórios Markdown | 0% |
| **Total estimado (média simples)** | **68%** |

O percentual do menu acompanha os três algoritmos disponíveis dos quatro previstos
(BFS, DFS, UCS e A*). Os três disponíveis já oferecem os modos nome e conteúdo.
