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
| [Validação com Docencia/Fontes](docs/VALIDACAO_DOCENCIA.md) | Resultados das três etapas no acervo real de PDFs e limites de extração. |
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
│   ├── METODOLOGIA.md
│   └── VALIDACAO_DOCENCIA.md
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

BFS/DFS compartilham o motor `_percorrer` para descoberta, custos, visitas e
fila/pilha. `buscar` define uma tarefa com alvo; `mapear` define a varredura
completa. A inserção direta das subpastas na deque dispensa uma lista temporária;
somente a inserção do DFS é invertida, preservando a descoberta dos arquivos.
As buscas validam e normalizam o alvo antes de acessar diretórios ou preparar
a heurística. Isso impede que um tipo inválido chegue ao cálculo de bigramas.

UCS/A* compartilham um motor de heap, com g separado da prioridade. O custo de
uma pasta só se torna conhecido ao expandi-la: entradas pendentes usam o custo
do pai, acrescido de h no A*. Objetivos confirmados retornam ao heap com g exato
e h=0. Essa avaliação
adiada evita listagens antecipadas não contabilizadas. Portanto, UCS minimiza
o custo acumulado sob as hipóteses documentadas; não ordena por um tamanho local
conhecido gratuitamente.

A heurística utiliza Jaccard de bigramas entre o nome da pasta e o termo. Sua
escala é controlada por alfa, na unidade de g, sem conversão automática. Ela não
é admissível em geral: A* não garante custo ótimo, menor tempo ou redução de
expansões. Alfa zero reproduz UCS. A formulação, a demonstração de correção de UCS
e os diagramas estão em [ARQUITETURA.md](docs/ARQUITETURA.md).

### 6.1. Fórmula da heurística h(n), sem modelos de ML

Seja `B(s)` o conjunto de pares consecutivos de caracteres de `s.casefold()`.
Se o texto normalizado tiver um caractere, usa-se esse caractere como token;
texto vazio produz conjunto vazio.
Para o diretório n e o termo pesquisado, calcula-se:

```text
A = B(nome_da_pasta(n))
T = B(termo)
J(A,T) = |A ∩ T| / |A ∪ T|       (J = 1 se ambos forem vazios)
h(n) = alfa × (1 − J(A,T))
f(n) = g(n) + h(n)
```

O cálculo utiliza somente o nome da pasta, sem ler arquivos nem utilizar modelos
de aprendizado de máquina. Com termo `pedagogia` e alfa=1000, a pasta
`_planos_pedagogicos_2024` recebe h≈666,667, enquanto `_imagens_auxiliares`
recebe h≈916,667. O primeiro nome recebe menor penalidade; isso não prova que
contenha o termo nem implica h próximo de zero. O desenvolvimento numérico está
na [seção 4.3 da arquitetura](docs/ARQUITETURA.md#43-heurística-e-adaptação-de-a).

Na implementação com avaliação adiada, pastas pendentes usam `g_pai+h(n)` até
conhecer o custo local. Objetivos confirmados usam g exato e h=0, portanto f=g.

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
consistentes entre as estratégias. As comparações por conteúdo abaixo explicitam
as duas quantidades exigidas para avaliar o efeito da heurística.

### 9.1. Demonstração de poda: UCS versus A*

```text
ΔN = pastas_abertas_UCS − pastas_abertas_A*
ΔL = arquivos_lidos_UCS − arquivos_lidos_A*
```

| Cenário | Palavra / alfa do A* | Pastas UCS / A* | ΔN | Arquivos lidos UCS / A* | ΔL |
| --- | --- | ---: | ---: | ---: | ---: |
| Árvore didática padrão | algoritmo / 100 | 41 / 41 | 0 | 52 / 52 | 0 |
| Cenário controlado de pedagogia | pedagogia / 1000 | 3 / 2 | 1 | 2 / 1 | 1 |
| Acervo real `../Docencia/Fontes` | algoritmo / 100 | 10 / 10 | 0 | 50 / 50 | 0 |

No cenário de pedagogia, A* abriu uma pasta a menos (redução de 33,33%) e leu
um arquivo a menos (50%), retornando o mesmo arquivo e custo que UCS. O teste
reproduzível está em [test_astar.py](tests/test_astar.py), executado com
`python3 -m tests.test_astar`. A árvore padrão e o acervo real não apresentaram
redução nessas configurações. A comparação quantitativa e o contraexemplo em
que A* retorna custo maior constam na [metodologia](docs/METODOLOGIA.md).

Nesta demonstração, “poda” designa pastas e leituras evitadas pela ordem de busca
e parada antecipada. Não há exclusão permanente de pastas pelo nome. O contador
`arquivos_lidos` registra arquivos efetivamente abertos/lidos pela aplicação em
uma execução; não conta acessos físicos ao disco, pois o cache pode atendê-los.

Essas observações sustentam a análise de cenários, não uma superioridade geral.
A árvore deve permanecer estática; a verificação de symlinks não impede trocas
concorrentes entre verificar e abrir. Texto é classificado por extensão, a
extração PDF possui limitações e o pico medido não corresponde à memória total
do processo. A [validação com o acervo real Docencia/Fontes](docs/VALIDACAO_DOCENCIA.md)
processou 62 PDFs, conferiu as três etapas e documentou sete arquivos sem texto
extraível, além de avisos de codificação de fontes. Esses casos limitam a busca
textual nesta configuração. As tabelas de referência e sua reprodução encontram-se
na [metodologia experimental](docs/METODOLOGIA.md).

### 9.2. Trabalho futuro: suporte complementar a fontes de PDF

Propõe-se avaliar **fontTools** como dependência opcional para auxiliar o pypdf
na interpretação de determinadas fontes incorporadas. A motivação são os avisos
observados no acervo e a possibilidade de melhorar a fidelidade dos caracteres,
reduzindo falsos negativos na pesquisa por conteúdo. Esse benefício ainda precisa
ser comprovado com documentos de referência; fontTools não substitui OCR nos
arquivos que armazenam palavras apenas como imagens ou contornos vetoriais.

A biblioteca não foi instalada nem ativada. A avaliação futura deverá conferir
compatibilidade com o Python usado, fixar a versão e comparar texto, resultados,
tempo e memória em ambientes equivalentes. O suporte permaneceria isolado na
extração PDF, preservando os algoritmos. As justificativas, referências e o
protocolo proposto estão na [seção 5.1 da arquitetura](docs/ARQUITETURA.md#51-possível-uso-futuro-de-fonttools).

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

## 11. Processo de desenvolvimento e consolidação

O projeto foi construído incrementalmente, com verificações executáveis e registro
das decisões em [AGENTS.md](AGENTS.md) e [HISTORICO.md](HISTORICO.md):

1. **Modelagem e base:** definimos diretório como nó, expansão por `os.scandir`,
   descoberta no pai, exclusão de symlinks e campos da dataclass de métricas.
   Criamos o gerador determinístico para comparar estratégias sobre os mesmos dados.
2. **Busca cega:** implementamos BFS/DFS com deque e verificamos a ordem de visita,
   a descoberta dos arquivos e a separação entre mapeamento completo e busca com alvo.
3. **Custo uniforme:** acrescentamos UCS com heap e avaliação adiada, pois o custo
   em itens só é conhecido ao abrir a pasta. Testes com objetivos mais baratos
   conferiram a seleção por custo acumulado e os desempates.
4. **Conteúdo, heurística e formatos:** centralizamos a leitura em blocos e o
   custo em bytes; A* reutilizou o motor de heap com Jaccard de bigramas. Testes
   demonstraram economia e um contraexemplo de ótimo. Depois, a extensão PDF
   autorizada foi isolada em um adaptador, com limitações explícitas sem OCR.
5. **Instrumentação e entregas:** separamos as chamadas de tempo e memória,
   conferimos sua equivalência e produzimos JSONs auditáveis e tabelas por etapa.
   Impressão e persistência ficaram fora do cronômetro.
6. **Validação e revisão:** usamos cenários com custos conhecidos, oráculos
   independentes e o acervo real de 62 PDFs. Na consolidação, unificamos o percurso
   BFS/DFS, removemos listas temporárias e corrigimos a validação de alvos na API.
   Oito percursos preservaram resultados, contadores e rastros antes/depois.

As justificativas e os compromissos de cada decisão estão na
[síntese da arquitetura](docs/ARQUITETURA.md#31-síntese-das-decisões-de-arquitetura).
A [metodologia](docs/METODOLOGIA.md#74-verificação-da-revisão-de-código) registra
a comparação local de memória da revisão; os tempos históricos do acervo real
continuam vinculados à revisão identificada no relatório original.
