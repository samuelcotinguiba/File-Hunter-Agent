# File Hunter Agent

Projeto didático em Python 3 para comparar buscas em árvores de diretórios.
Estão implementados: estrutura, listagem segura, métricas, gerador de dados,
BFS, DFS, UCS e A* por nome ou conteúdo, menu e argumentos, persistência JSON e
relatórios Markdown. As entregas estão registradas em [HISTORICO.md](HISTORICO.md).
As buscas e os textos usam biblioteca padrão (Python 3.7+). A extração de PDF
usa **pypdf**, dependência externa opcional autorizada posteriormente; requer
Python 3.9+ na versão fixada. A arquitetura das buscas permanece a mesma.

Para habilitar PDF sem alterar o Python do sistema:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# Alternativa: ative o ambiente para usar python normalmente.
source .venv/bin/activate
```

Nos comandos abaixo, use `.venv/bin/python` no lugar de `python3` quando quiser
ler PDFs. A suíte com esse Python também executa os testes extras do extrator.

Execute a partir de `File-Hunter-Agent/`:

```sh
python3 gerar_arvore.py
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo bfs
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo dfs
python3 main.py --raiz ./docencia/fontes --alvo livro --algoritmo ucs
python3 main.py --raiz ./docencia/fontes --alvo algoritmo --algoritmo ucs --modo conteudo
python3 main.py --raiz ./docencia/fontes --alvo algoritmo --algoritmo astar --modo conteudo --alfa 100
python3 main.py
python3 -m funcoes.relatorio resultados --saida resultados/relatorio.md
python3 -m tests.test_buscas
python3 -m tests.test_ucs
python3 -m tests.test_conteudo
python3 -m tests.test_astar
python3 -m tests.test_relatorio
python3 -m tests.test_formatos
.venv/bin/python -m tests.test_pdf
python3 -m tests.test_comparacao
python3 -m tests
python3 -c 'from funcoes.listagem import listar_dir; print([e.name for e in listar_dir("docencia/fontes")])'
```

O gerador cria 40 pastas abaixo de `docencia/fontes/`, com profundidade máxima
de quatro níveis e 64 arquivos .txt, .md, .py e .png. A seed é 2024. Apenas parte
dos arquivos de texto contém `algoritmo`. A árvore gerada e os JSON de execuções
são ignorados pelo Git, assim como os relatórios gerados em resultados/.
Novas execuções do gerador sobrescrevem apenas seus arquivos conhecidos.

`listar_dir(caminho)` retorna `os.DirEntry` ordenados por nome, sem links
simbólicos. Erros de acesso são propagados. A listagem não atualiza contadores.
`Metricas` guarda contadores e custo; `medir_tempo` e `medir_memoria` retornam
`(resultado, medição)`. Execute cada auxiliar com estado novo e separado.

`--modo nome` é o padrão na CLI. No menu, escolha algoritmo e modo, depois informe
o termo. A busca por conteúdo considera formatos textuais, inclusive extensões
em maiúsculas, usa UTF-8 com `errors="ignore"` e não diferencia maiúsculas no
termo. A classificação é por extensão, conforme `EXTENSOES_TEXTO`.
São lidos todos os textos de cada pasta expandida; g soma os bytes reais dessas
leituras no caminho da raiz até a pasta objetivo, incluindo ambas. O tamanho em
bytes é obtido do deslocamento binário ao terminar a leitura, preservando a
contagem de acentos, sequências inválidas e CRLF.
O contador `arquivos_lidos` abrange toda a exploração, inclusive ramos fora do
caminho final. Textos simples são lidos até o fim em blocos de 64 Ki caracteres,
uma vez por execução. A memória dessa leitura é O(tamanho do bloco + tamanho do
termo), sem cache entre as duas execuções de medição. PDF tem leitura por parser
e pode reler trechos após seek; o custo soma esses bytes efetivamente entregues
ao extrator. PDF não tem a mesma garantia de memória limitada dos textos simples.

## Subpastas, PDF e outros formatos

As quatro buscas percorrem subpastas a partir de `--raiz`, sem limite de níveis
definido pela aplicação e sem seguir symlinks. No modo nome, qualquer arquivo
regular pode ser encontrado: PDF, DOCX, XLSX, PPTX, ZIP, PNG, executáveis e arquivos
sem extensão. A pesquisa verifica se o nome contém o termo; não usa glob.

```sh
# Troque a raiz pela pasta real dos seus documentos.
python3 main.py --raiz /caminho/dos/documentos --alvo .pdf --algoritmo bfs --modo nome
python3 main.py --raiz /caminho/dos/documentos --alvo relatorio --algoritmo dfs --modo nome
```

Isso busca inclusive nas subpastas, mas encerra na pasta objetivo escolhida pelo
algoritmo: retorna todos os nomes correspondentes dessa pasta. Não coleta todos
os resultados de toda a árvore. O termo `.pdf` também pode ocorrer no meio do nome,
por exemplo `relatorio.pdf.bak`, pois a regra original é correspondência parcial.

| Modo | Formatos | O que é pesquisado |
| --- | --- | --- |
| nome | Qualquer extensão ou sem extensão | Nome do arquivo, sem abrir seu conteúdo |
| conteudo | TXT/MD/RST, CSV/TSV, JSON/JSONL, LOG, XML/HTML/SVG, CSS/JS/TS, YAML, INI/CFG/TOML, SQL/TEX e fontes | Texto UTF-8 decodificado |
| conteudo | PDF com texto extraível | Todas as páginas, usando pypdf opcional |
| conteudo | DOC/DOCX, XLS/XLSX, PPT/PPTX, ZIP e imagens binárias | Extração interna não implementada; use nome para localizar |

Lista completa dos sufixos textuais: `.txt`, `.md`, `.rst`, `.py`, `.csv`, `.tsv`,
`.json`, `.jsonl`, `.log`, `.xml`, `.html`, `.htm`, `.svg`, `.css`, `.js`, `.ts`,
`.yaml`, `.yml`, `.ini`, `.cfg`, `.toml`, `.sql`, `.tex`, `.sh`, `.c`, `.cpp`, `.h`,
`.java`, `.go`, `.rs`. Arquivos sem extensão não são lidos no modo conteúdo.
PDF não é pesquisado como UTF-8 bruto: `funcoes/pdf.py` extrai texto por página,
incluindo PDFs com conteúdo comprimido. Falta da dependência gera orientação de
instalação ao encontrar PDF no modo conteúdo; buscas por nome continuam funcionando.
PDFs protegidos por senha ou corrompidos geram erro com o caminho. Não há OCR:
PDF digitalizado sem camada textual pode não produzir texto. Veja as limitações
na [documentação oficial de extração do pypdf](https://pypdf.readthedocs.io/en/stable/user/extract-text.html).
Office e OCR não foram incluídos na autorização/implementação de PDF.

Para a etapa 3, o alvo é encontrado pelo conteúdo, não pelo nome do arquivo.
O teste com `pedagogia` usa `documento.txt` em `_planos_pedagogicos_2024/` e um
`catalogo.log` em `_imagens_auxiliares/`: com alfa=1000, A* leu 1 arquivo e abriu
2 pastas; UCS leu 2 arquivos e abriu 3 pastas, retornando o mesmo custo de caminho.
A similaridade reduz a estimativa da pasta pedagógica em relação à de imagens;
não exige que seu valor absoluto seja zero. O contraexemplo de custo maior para
A* permanece nos testes, pois essa economia é dependente do cenário e do peso.

## JSON e relatórios

Cada busca pelo menu/CLI salva automaticamente um JSON em `resultados/` depois
das medições. Use `--sem-salvar` para somente consultar, ou `--resultados PASTA`
para mudar o destino. Mantenha esse destino fora da raiz da busca para não alterar
os dados das comparações. Arquivos têm nomes exclusivos e não sobrescrevem
execuções anteriores. Erros de busca não produzem um registro de sucesso.

O esquema `versao=1` contém `instante_utc`, `parametros` (raiz, alvo, algoritmo,
modo, alfa, extensoes_texto, extrator_pdf), `encontrados` (lista retornada),
`metricas` e `avaliacao_final`. Alfa é null fora de A*.
UTF-8 preserva acentos; métricas não finitas ou negativas são rejeitadas.
O novo campo `extensoes_texto` registra quais sufixos participaram do custo em
bytes; no modo nome ele é null. JSONs antigos continuam aceitos e mostram
"não registrado" para essa configuração. Compare a mesma seleção de extensões,
além de raiz, termo e modo, pois acrescentar formatos pode mudar custo e resultados.
O campo `extrator_pdf` identifica a versão utilizada; `avaliacao_final` registra
g, h=0 e f=g no objetivo UCS/A*, ou null sem objetivo. Ambos são opcionais para
compatibilidade com JSONs antigos. Versões diferentes do parser podem mudar
extração e releituras, portanto compare a mesma configuração.

```sh
# Converter todos os JSON da pasta em duas tabelas vinculadas pelo ID.
python3 -m funcoes.relatorio resultados --saida resultados/relatorio.md
# Selecionar arquivos específicos ou imprimir sem gravar Markdown.
python3 -m funcoes.relatorio resultados/execucao_EXEMPLO.json
```

Substitua o nome EXEMPLO por um arquivo existente. A leitura de diretório não é
recursiva. Entradas repetidas são deduplicadas por realpath. JSON corrompido ou
incompatível encerra a conversão com o caminho do erro; não gera tabela parcial.
Parâmetros e métricas usam o mesmo ID. `Retornados` conta os arquivos da pasta
objetivo escolhida; `Encontrados` inclui candidatos descobertos que UCS/A* podem
não selecionar. `g` usa itens ou bytes, conforme o modo. Ausência de resultado é
lista vazia com g=0, não um erro de acesso.

## Comparação reproduzível

Para a tabela solicitada da etapa 3, execute diretamente:

```sh
.venv/bin/python main.py --comparar --alvo algoritmo --alfa 100 --resultados resultados/comparacao
.venv/bin/python -m funcoes.relatorio resultados/comparacao --comparativo --saida resultados/comparacao/tabela.md
```

`--comparar` usa conteúdo e executa UCS/A* sequencialmente; não combine com
`--algoritmo` ou `--modo nome`. Sem --alvo, usa algoritmo. --sem-salvar permite
mostrar a tabela sem criar JSON. A função `comparar_conteudo` não grava arquivos.

As sete colunas são **Algoritmo**, **Palavra no Conteúdo**, **Caminho**,
**Pastas Abertas**, **Arquivos Lidos do Disco**, **Custo Total f(n)** e **Tempo (ms)**.
O relatório geral também acrescenta a tabela quando há execuções UCS/A* de
conteúdo para algoritmo. Outras palavras podem ser selecionadas no conversor
com `--comparativo --alvo TERMO`. Cada linha é uma execução; selecione os JSONs
do experimento desejado. Raízes, seleções de texto e versões PDF distintas são
agrupadas separadamente, inclusive dados antigos com configuração não registrada.

f(n)=g(n)+h(n). UCS usa h=0; no objetivo confirmado de A*, h=0 e f final=g em
bytes. Isso é o custo do caminho, não o total de bytes de todos os ramos abertos.
Sem objetivo, Caminho é Não encontrado e f aparece como —. O campo de arquivos
lidos representa arquivos abertos/lidos pela aplicação; o cache do sistema pode
evitar acesso físico ao disco. As duas chamadas para medir tempo e memória não
dobram os contadores apresentados. Não se deve concluir desempenho geral de uma
única amostra de tempo, pois a segunda busca pode aproveitar o cache da primeira.

Gere a árvore e execute sequencialmente, mantendo raiz, alvo e modo iguais:

```sh
python3 gerar_arvore.py
python3 main.py --alvo livro --algoritmo bfs
python3 main.py --alvo livro --algoritmo dfs
python3 main.py --alvo livro --algoritmo ucs
python3 main.py --alvo livro --algoritmo astar --alfa 100
python3 -m funcoes.relatorio resultados --saida resultados/relatorio.md
```

Para conteúdo, repita os quatro comandos com `--modo conteudo --alvo algoritmo`.
O relatório inclui todos os JSON existentes, portanto selecione os arquivos do
experimento desejado ou use uma pasta de resultados específica por experimento.
Tempos são amostras locais, sujeitos a cache e carga; não são uma classificação
geral dos algoritmos. Cada comando executa a busca duas vezes, para medir tempo
sem tracemalloc e memória em outra chamada. Contadores refletem uma execução.

Na verificação final sobre a árvore gerada:

| Algoritmo | Pastas por nome (livro) | g (itens) | Pastas por conteúdo (algoritmo) | g (bytes) |
| --- | ---: | ---: | ---: | ---: |
| BFS | 30 | 17 | 30 | 320 |
| DFS | 5 | 17 | 5 | 320 |
| UCS | 41 | 17 | 41 | 320 |
| A* (alfa=100) | 30 | 17 | 41 | 320 |

Esses resultados descrevem esta árvore: todos os arquivos-alvo têm a mesma
profundidade e há custos iguais. Não demonstram superioridade universal de DFS
ou A*. Os testes incluem árvores onde UCS retorna custo menor e onde A* retorna
custo maior, conforme registrado no histórico.

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
- **A*:** compartilha o motor de heap com UCS. A prioridade de uma pasta pendente
  é g do pai + h da pasta, pois seu custo local só é conhecido ao expandi-la.
  O custo real g permanece separado da prioridade. Objetivos já confirmados são
  reinseridos com g exato e h=0. Essa avaliação adiada contabiliza toda abertura.
  Com `--alfa 0`, o resultado e os contadores reproduzem UCS.
- **Leitura compartilhada:** `examinar_arquivos` aplica o mesmo critério de texto,
  correspondência e custo para BFS, DFS, UCS e A*. Não duplica leituras para medir bytes.
  `ler_texto` usa a decodificação incremental do próprio `open` e mantém a cauda
  após casefold para termos entre blocos. Mesmo um alvo encontrado no começo não
  interrompe a leitura, pois o custo inclui todos os bytes do arquivo. Após
  encontrar o termo, libera a janela de comparação enquanto consome o restante.
- **Ciclos:** conjunto de realpaths marcados ao inserir na fronteira.
- **Custos e heurística:** Jaccard de conjuntos de bigramas após casefold,
  h=alfa*(1-similaridade(nome_pasta, termo)). Bigramas do termo são preparados uma
  vez por busca. Alfa deve ser finito e não negativo; padrão 1. A heurística não
  é admissível: A* não garante caminho ótimo. Peso maior pode mudar muito a ordem;
  sua escala depende da unidade de g, itens ou bytes. Nomes diferentes não provam
  ausência de um alvo, portanto a heurística não elimina pastas permanentemente.
- **Relatórios:** dicionários/listas serializáveis com versão explícita; leitura
  e validação independentes das buscas. Duas tabelas evitam misturar parâmetros
  longos com contadores. Persistência fora da medição evita contaminar resultados.

### Módulos e dependências

| Módulo | Responsabilidade e justificativa |
| --- | --- |
| main.py | Interface e coordenação; a função executar não grava arquivos. |
| listagem.py | Contrato único de listagem ordenada e verificação de symlinks. |
| conteudo.py | Critérios de correspondência e custo local, sem política de fronteira. |
| pdf.py | Adaptador opcional pypdf, extração por página e contagem de bytes por leitura. |
| bfs_dfs.py | Políticas de fila/pilha sobre a mesma regra de descoberta. |
| ucs.py | Motor de heap, avaliação adiada e confirmação de objetivos por custo. |
| heuristica.py | Similaridade pura e preparação do estimador sem acesso ao disco. |
| astar.py | Configura o motor de heap com estimador, preservando g separado de f. |
| metricas.py | Contadores e instrumentação opcionais, sem interface nem persistência. |
| relatorio.py | Esquema JSON, gravação e apresentação Markdown sem executar buscas. |
| requirements.txt | Única dependência externa direta, fixada para extração PDF. |
| gerar_arvore.py | Dados reproduzíveis, sem dependência dos algoritmos. |

Não há árvore de objetos BST: os caminhos representam diretórios e a fronteira
armazena apenas dados necessários à busca. UCS e A* compartilham o mecanismo
porque diferem na prioridade, mantendo as garantias distintas documentadas.

### Custo das estruturas

Para uma pasta com k entradas, scandir percorre O(k) e a ordenação custa
O(k log k), com O(k) referências. Isso torna os testes e desempates reproduzíveis.
deque insere/remove nas extremidades em O(1); heap usa O(log F) por operação,
onde F é o número de entradas da fronteira. A estrutura de visitados é um conjunto
com consultas em O(1) esperado; armazena O(D) realpaths para D pastas descobertas.
Mesmo em DFS, fronteira e visitados podem crescer até O(D); não se promete
memória total proporcional apenas à profundidade.

Leitura de conteúdo percorre todos os bytes dos textos das pastas abertas, com
blocos e cauda de sobreposição, evitando manter arquivos inteiros em memória.
Os conjuntos de bigramas são lineares no comprimento dos nomes/termo; o termo
é preparado uma vez. O heap usa um contador monotônico para nunca comparar nós
complexos em empates. Os testes verificam invariantes e oráculos independentes,
além da execução completa de buscas, persistência e apresentação.

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
- **PDF opcional:** a biblioteca é carregada antes da medição; importação não é
  cobrada só da primeira busca. Arquivo é aberto uma vez, páginas são extraídas
  integralmente e o wrapper soma bytes de leituras e releituras do parser.
  O parser mantém estruturas próprias em memória, portanto esse consumo depende
  do PDF. Não há dependência pypdf nas políticas de fronteira nem nas métricas.

A arquitetura mantém os critérios exigidos e explicita os compromissos: custo
de caminho difere do trabalho total, heurística não garante ótimo, e medições
dependem de árvore estática e do ambiente. Os artefatos permanecem reproduzíveis
pelo gerador, pelos parâmetros registrados e pela suíte `python3 -m tests`.

## Progresso estimado

Percentuais representam funcionalidades entregues, não cobertura de testes ou
tempo restante. Cada linha tem o mesmo peso; escopo futuro ainda pode ser refinado.

| Entrega | Concluído |
| --- | ---: |
| Base do passo A | 100% |
| BFS e DFS por nome | 100% |
| UCS por nome (etapa 2) | 100% |
| Busca por conteúdo e custo em bytes (etapa 3) | 100% |
| Heurística e A* | 100% |
| Menu e CLI para todos os algoritmos | 100% |
| JSON e relatórios Markdown | 100% |
| **Total do escopo implementado (média simples)** | **100%** |

O menu oferece os quatro algoritmos (BFS, DFS, UCS e A*) nos modos nome e conteúdo.
Persistência, relatórios, justificativa da arquitetura e verificações do escopo
estão concluídos. 100% indica entregas implementadas e verificadas, não ausência
garantida de defeitos nem cobertura de todos os sistemas de arquivos possíveis.
