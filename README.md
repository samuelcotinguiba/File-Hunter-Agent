# File Hunter Agent

## Resumo

O File Hunter Agent é um projeto experimental em Python para comparar estratégias
de busca em árvores de diretórios. A implementação integra busca em largura
(BFS), busca em profundidade (DFS), busca de custo uniforme (UCS) e busca orientada
por heurística (A*). O estudo considera três tarefas: mapeamento completo,
localização por nome e localização por conteúdo. A avaliação utiliza expansões
de diretórios, itens examinados, arquivos lidos, custo do caminho, tempo decorrido
e pico de alocações Python. A arquitetura separa interface, políticas de busca,
acesso a arquivos, instrumentação e produção de relatórios.

**Palavras-chave:** busca em grafos; estruturas de dados; sistemas de arquivos;
heurísticas; avaliação experimental.

## 1. Objetivos e delimitação

O objetivo geral consiste em analisar como a política de exploração influencia
a descoberta de arquivos e o trabalho realizado sobre o sistema de arquivos.
Os objetivos específicos são:

1. Comparar a ordem de descoberta de BFS e DFS em um mapeamento integral.
2. Comparar quatro estratégias para localizar um termo no nome de um arquivo.
3. Investigar o efeito de uma heurística lexical na busca por conteúdo.
4. Registrar métricas verificáveis e relatórios reproduzíveis por etapa.
5. Justificar as estruturas de dados e os compromissos da implementação.

O nó de busca corresponde a um diretório. Sua expansão consiste em listar o
conteúdo com `os.scandir`; um arquivo é descoberto quando aparece na expansão
do diretório pai. A correspondência usa substring após `casefold`, sem distinção
entre maiúsculas e minúsculas. Não há classes de árvore binária de busca, modelos
de aprendizado de máquina ou dependência de Matplotlib.

O mapeamento completo é exclusivo de BFS/DFS na etapa 1. As demais tarefas são
orientadas ao objetivo, embora possam explorar toda a árvore quando necessário.
As condições de correção pressupõem uma árvore finita, acessível e estática.

## 2. Organização da documentação

| Documento | Finalidade |
| --- | --- |
| [Arquitetura e modelo computacional](docs/ARQUITETURA.md) | Visões de módulos e execução, custos, heurística, invariantes e complexidade. |
| [Metodologia experimental](docs/METODOLOGIA.md) | Protocolo de medição, critérios de comparação, resultados de referência e ameaças à validade. |
| [AGENTS.md](AGENTS.md) | Contratos de manutenção e decisões que devem ser preservadas. |
| [HISTORICO.md](HISTORICO.md) | Evolução da implementação, correções e evidências das verificações. |

A documentação descreve o comportamento implementado. Garantias condicionais,
resultados observados e possibilidades de trabalho futuro são apresentados
separadamente. A redação acadêmica não constitui declaração de conformidade
com uma norma editorial específica.

## 3. Organização do projeto

```text
File-Hunter-Agent/
├── AGENTS.md
├── README.md
├── HISTORICO.md
├── main.py
├── gerar_arvore.py
├── requirements.txt
├── docs/
│   ├── ARQUITETURA.md
│   └── METODOLOGIA.md
├── funcoes/
│   ├── __init__.py
│   ├── listagem.py
│   ├── metricas.py
│   ├── bfs_dfs.py
│   ├── ucs.py
│   ├── heuristica.py
│   ├── astar.py
│   ├── conteudo.py
│   ├── pdf.py
│   └── relatorio.py
├── tests/
├── resultados/              # JSON e Markdown produzidos pelas execuções
└── docencia/fontes/         # conjunto de dados gerado localmente
```

O núcleo utiliza a biblioteca padrão, incluindo `dataclasses` para `Metricas`.
A extração de PDF é uma extensão opcional autorizada posteriormente e depende
de **pypdf**, biblioteca externa fixada em `requirements.txt`. Dados gerados,
ambientes virtuais e resultados locais são ignorados pelo Git.

## 4. Ambiente e execução

O ambiente usado nas verificações documentadas é Python 3.9.6. O núcleo emprega
recursos disponíveis a partir do Python 3.7; essa indicação não representa uma
matriz de testes de todas as versões. A extensão PDF fixada requer Python 3.9+.
Execute os comandos a partir da pasta `File-Hunter-Agent/`.

```sh
python3 gerar_arvore.py
python3 -m tests
python3 main.py
```

O gerador utiliza seed 2024 e produz 40 diretórios abaixo da raiz, profundidade
máxima de quatro níveis e 64 arquivos `.txt`, `.md`, `.py` e `.png`. A expansão
integral inclui a raiz: portanto, são contabilizadas 41 pastas abertas.
A reexecução sobrescreve os arquivos conhecidos do gerador e não remove arquivos
adicionais; a reprodução dos números de referência pressupõe uma árvore sem
alterações externas.

Para habilitar extração de PDF em ambiente virtual:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m tests
```

Os exemplos usam caminhos de ambiente virtual para sistemas POSIX. A suíte com
`python3` verifica o núcleo e, na ausência de pypdf, informa que a extração PDF
não foi executada. O Python da `.venv`, com a dependência instalada, verifica
também o extrator. Não executar testes com `-O`, pois as asserções seriam removidas.

## 5. Etapas e produtos de avaliação

| Etapa | Estratégias | Critério de encerramento | Produtos |
| --- | --- | --- | --- |
| 1 — Mapeamento | BFS e DFS | Esgotamento da fronteira | Todos os caminhos em ordem, primeiros 10 lado a lado, percursos, totais, tempo e memória. |
| 2 — Nome | BFS, DFS, UCS e A* | Pasta objetivo selecionada pela estratégia | Primeiro arquivo correspondente, g acumulado, tabela comparativa e decomposição dos custos. |
| 3 — Conteúdo | UCS e A* | Retirada da candidatura objetivo do heap | Caminho, N, arquivos lidos, f final, tempo, métricas complementares e diferença de expansões/leituras. |

```sh
python3 main.py --etapa 1 --resultados resultados/entregas/etapa1
python3 main.py --etapa 2 --alvo livro --alfa 100 --resultados resultados/entregas/etapa2
.venv/bin/python main.py --etapa 3 --alvo algoritmo --alfa 100 --resultados resultados/entregas/etapa3
```

Os alvos padrão são `livro` na etapa 2 e `algoritmo` na etapa 3. O peso padrão
é `alfa=1`; o valor 100 acima é um parâmetro dos experimentos de referência.
`--comparar` equivale à etapa 3. Cada etapa salva JSONs exclusivos e atualiza
`etapa_N.md` no destino. `--sem-salvar` desativa a gravação. No menu, as opções
5, 6 e 7 executam as etapas; as opções 1 a 4 executam buscas individuais.

A etapa define seus algoritmos e modo: não deve ser combinada com `--algoritmo`
ou modo incompatível. A etapa 1 não recebe alvo nem alfa. Na busca por nome,
retorna-se um arquivo; a listagem completa da pasta objetivo é contabilizada,
por isso o número de correspondências descobertas pode ser maior que o retorno.

Para testar outro conjunto de documentos, selecione a raiz sem modificar o código:

```sh
python3 main.py --etapa 1 --raiz /caminho/dos/documentos --resultados resultados/nova_pasta/etapa1
python3 main.py --etapa 2 --raiz /caminho/dos/documentos --alvo livro --resultados resultados/nova_pasta/etapa2
.venv/bin/python main.py --etapa 3 --raiz /caminho/dos/documentos --alvo algoritmo --alfa 100 --resultados resultados/nova_pasta/etapa3
```

O destino dos resultados deve ficar fora da raiz pesquisada. A classificação
por nome aceita qualquer arquivo regular, inclusive PDF, Office, imagens e
arquivos sem extensão. A pesquisa por conteúdo lê os sufixos de
`EXTENSOES_TEXTO`, em [conteudo.py](funcoes/conteudo.py), e PDFs com texto extraível
quando pypdf está disponível. Conteúdo de Office, arquivos compactados e OCR
não estão implementados. PDF somente imagem pode não oferecer texto pesquisável;
essa limitação decorre da modalidade de extração adotada ([documentação do pypdf](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)).

Buscas individuais também aceitam `--algoritmo`, `--modo` e `--alvo`:

```sh
python3 main.py --raiz ./docencia/fontes --algoritmo bfs --modo nome --alvo .png
.venv/bin/python main.py --raiz ./docencia/fontes --algoritmo astar --modo conteudo --alvo algoritmo --alfa 100
```

A correspondência é parcial, sem glob ou expressão regular: `.pdf` também pode
ocorrer no meio do nome de um arquivo.

## 6. Estruturas de dados e justificativas de design

A solução adota uma arquitetura modular em um único processo. A interface
coordena as execuções; os algoritmos definem a fronteira; listagem e conteúdo
concentram o acesso a arquivos; as métricas instrumentam a chamada; os relatórios
persistem e apresentam os resultados. Essa decomposição permite verificar as
políticas de busca com custos conhecidos sem executar o menu.

| Estrutura ou mecanismo | Aplicação e justificativa |
| --- | --- |
| `collections.deque` | FIFO com `popleft()` no BFS e LIFO com `pop()` no DFS, evitando deslocamentos de uma lista usada como fila. |
| `heapq` | Fronteira de UCS/A*, com tuplas `(prioridade, contador, nó)` para desempate estável. |
| `set` de realpaths | Controle de diretórios descobertos, sem seguir symlinks. |
| `os.DirEntry` e lista ordenada | Listagem compartilhada, com ordem determinística e exclusão de entradas não elegíveis. |
| `dataclass Metricas` | Contadores explícitos, valores iniciais zero e unidades centralizadas. |
| Dicionários e listas | Registros JSON, cronologia e rastros de expansão verificáveis. |
| Leitura em blocos | Textos UTF-8 com `errors="ignore"`, sem manter o arquivo inteiro em memória. |

BFS/DFS compartilham os critérios de descoberta e exame. UCS/A* compartilham
um motor de heap, com g separado da prioridade. O custo de uma pasta só se torna
conhecido ao expandi-la: entradas pendentes usam o custo do pai, acrescido de h
no A*. Objetivos confirmados retornam ao heap com g exato e h=0. Essa avaliação
adiada evita listagens antecipadas não contabilizadas. Portanto, UCS minimiza
o custo acumulado sob as hipóteses documentadas; não ordena por um tamanho local
conhecido gratuitamente.

A heurística utiliza Jaccard de bigramas entre o nome da pasta e o termo. Sua
escala é controlada por alfa, na unidade de g, sem conversão automática. Ela não
é admissível em geral: A* não garante custo ótimo, menor tempo ou redução de
expansões. Alfa zero reproduz UCS. A formulação, a demonstração de correção de UCS
e os diagramas estão em [ARQUITETURA.md](docs/ARQUITETURA.md).

## 7. Métricas e metodologia de medição

| Padrão | Campo | Definição |
| --- | --- | --- |
| Nós expandidos (N) | `pastas_abertas` | Diretórios efetivamente listados; `nos_expandidos` é um alias de leitura. |
| Arquivos/Itens examinados | `itens_examinados` | Arquivos e subpastas elegíveis presentes nas listagens. |
| Arquivos processados/lidos | `arquivos_lidos` | Arquivos cujo conteúdo foi lido na exploração; zero por nome. |
| Custo do Caminho g(n) | `custo_g` | Soma de itens ou bytes no caminho da raiz ao objetivo, incluindo ambos. |
| Consumo de Memória | `pico_mem_kb` | Pico rastreado por tracemalloc em KiB; não representa RSS. |
| Tempo de Execução | `tempo_ms` | Diferença de `time.perf_counter`, convertida para milissegundos. |

`arquivos_encontrados` registra correspondências descobertas; `encontrados`, no
JSON, contém os caminhos retornados. Na etapa 1, ambos se referem a todos os
arquivos. Sem objetivo, g permanece zero por convenção de armazenamento e f final
é apresentado como indefinido. No mapeamento não existe um único caminho objetivo.

Cada algoritmo é executado duas vezes com estado novo. Nos lotes, todos os tempos
são medidos antes dos perfis de memória; resultados, contadores e rastros são
comparados antes da montagem dos registros. O timer inclui a busca, a espera
por E/S, a heurística e o rastro solicitado. Menu, importações, impressão,
serialização e relatórios ficam fora do intervalo.

Trata-se de uma amostra por algoritmo, em ordem fixa, sem limpeza do cache do
sistema. Leituras contam operações da aplicação, não acessos físicos ao disco.
As tabelas acadêmicas das etapas 1/2 convertem memória para KB decimal; as métricas
principais preservam KiB. O protocolo completo, as colunas exigidas e as ameaças
à validade estão em [METODOLOGIA.md](docs/METODOLOGIA.md).

## 8. Persistência e relatórios

O esquema `versao=1` registra parâmetros, caminhos, métricas e metodologia. Nas
etapas, acrescenta experimento, base dos caminhos e expansões com diretório,
custo local e g. O campo `primeiros_10` preserva a cronologia do mapeamento.
Configuração de texto, versão do extrator e protocolo de medição permitem
separar comparações incompatíveis. Campos opcionais mantêm compatibilidade
com registros antigos, sem inventar informações ausentes.

JSONs são criados sem sobrescrever execuções anteriores. O conversor valida os
registros e gera Markdown sem refazer as buscas. A leitura de uma pasta de JSONs
não é recursiva. No relatório global, mais de uma execução do mesmo algoritmo
no mesmo grupo exige selecionar um JSON por algoritmo/experimento.

```sh
python3 -m funcoes.relatorio resultados/entregas/etapa1 --etapa 1 --saida resultados/entregas/etapa1/reconstruido.md
python3 -m funcoes.relatorio resultados/entregas/etapa2 --etapa 2 --alvo livro --saida resultados/entregas/etapa2/reconstruido.md
python3 -m funcoes.relatorio resultados/entregas/etapa3 --etapa 3 --alvo algoritmo --saida resultados/entregas/etapa3/reconstruido.md
```

`--comparativo` seleciona somente a comparação UCS/A* por conteúdo; `--alvo`
seleciona o termo. Sem `--etapa` ou `--comparativo`, o conversor gera o relatório
geral. JSON corrompido ou incompatível é reportado com o caminho de origem.

## 9. Evidências e limitações

A árvore padrão permitiu verificar cronologias distintas de BFS/DFS e custos
consistentes entre as estratégias. Na etapa 3, com alfa=100, UCS e A* expandiram
41 pastas e leram 52 arquivos cada: não houve economia de expansões nesse caso.
Um cenário controlado de pedagogia, com alfa=1000, registrou 3 pastas/2 leituras
para UCS e 2 pastas/1 leitura para A*, com o mesmo objetivo e custo. Outro teste
mostrou A* retornando custo maior, apesar de menos expansões.

Essas observações sustentam a análise de cenários, não uma superioridade geral.
A árvore deve permanecer estática; a verificação de symlinks não impede trocas
concorrentes entre verificar e abrir. Texto é classificado por extensão, a
extração PDF possui limitações e o pico medido não corresponde à memória total
do processo. A [validação com o acervo real Docencia/Fontes](docs/VALIDACAO_DOCENCIA.md)
processou 62 PDFs, conferiu as três etapas e documentou sete arquivos sem texto
extraível, além de avisos de codificação de fontes. Esses casos limitam a busca
textual nesta configuração. As tabelas de referência e sua reprodução encontram-se
na [metodologia experimental](docs/METODOLOGIA.md).

## 10. Estado das entregas

| Componente | Implementação verificada |
| --- | ---: |
| Base, gerador e listagem | 100% |
| Etapa 1 — BFS/DFS e cronologia global | 100% |
| Etapa 2 — Quatro estratégias e busca por nome | 100% |
| Etapa 3 — Conteúdo e comparação UCS/A* | 100% |
| Interface, persistência e relatórios | 100% |

Os percentuais indicam funcionalidades implementadas e verificadas segundo o
escopo informado. Não medem cobertura de testes, ausência de defeitos ou aprovação
docente. O histórico registra as correções e as limitações identificadas.
