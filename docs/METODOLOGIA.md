# Metodologia experimental e critérios de avaliação

[Apresentação do projeto](../README.md) · [Arquitetura e modelo computacional](ARQUITETURA.md)

## 1. Natureza do estudo e questões de investigação

O projeto constitui um estudo experimental controlado sobre estratégias de
busca aplicadas a diretórios. A avaliação combina cenários determinísticos,
oráculos de correção, testes de regressão e observações instrumentadas. Os
resultados caracterizam as árvores e parâmetros utilizados; não representam
uma classificação geral de desempenho dos algoritmos.

As questões que orientam a análise são:

| Questão | Comparação e evidência |
| --- | --- |
| Q1. Como a ordem de exploração altera a descoberta dos arquivos? | Cronologia completa e primeiros 10 de BFS/DFS na etapa 1. |
| Q2. Como custo acumulado e política de fronteira influenciam o objetivo selecionado? | Caminhos, g e expansões das quatro estratégias na etapa 2. |
| Q3. A heurística lexical reduz expansões e leituras por conteúdo? | Diferenças entre UCS/A* na etapa 3, incluindo casos de economia e ausência de economia. |
| Q4. Menor exploração implica menor custo do caminho? | Contraexemplo em que A* expande menos diretórios e retorna objetivo mais caro. |

Os pesos de heurística e a distribuição dos arquivos são variáveis do experimento.
Uma economia observada com determinado alfa não autoriza concluir que o mesmo
peso será adequado a outra árvore ou unidade de custo.

## 2. Variáveis e condições de controle

| Categoria | Elementos |
| --- | --- |
| Variáveis independentes | Estratégia, tarefa, termo e alfa no A*. |
| Caracterização do conjunto de dados | Raiz, profundidade, quantidade de diretórios, tipos, distribuição e conteúdo dos arquivos. |
| Variáveis dependentes | N, itens examinados, correspondências, arquivos lidos, g, f final, tempo e pico de memória. |
| Condições mantidas em cada comparação | Mesma raiz estática, mesmo termo/modo, política de extensões, extrator PDF e revisão do código. |
| Fatores de ambiente | Versão do interpretador, sistema de arquivos, cache, carga do sistema e armazenamento. |

A ordenação dos irmãos é determinística. As etapas usam ordem fixa de algoritmos:
BFS/DFS na etapa 1; BFS/DFS/UCS/A* na etapa 2; UCS/A* na etapa 3. O identificador
`experimento` vincula os registros de um lote. A versão do interpretador e as
características do equipamento não são automaticamente registradas no JSON;
devem acompanhar a descrição de novos experimentos no relatório acadêmico.

## 3. Conjuntos de dados e preparação

### 3.1. Árvore didática de referência

[gerar_arvore.py](../gerar_arvore.py) utiliza seed 2024 e um gerador congruencial
para definir parte do conteúdo. Produz 40 diretórios abaixo de `docencia/fontes/`,
64 arquivos e profundidade máxima de quatro níveis. O número de nós expandidos
no mapeamento é 41 porque inclui a raiz.

Os arquivos possuem extensões `.txt`, `.md`, `.py` e `.png`. Somente parte dos
textos contém `algoritmo`. Os grupos incluem `_planos_pedagogicos_2024`,
`_imagens_auxiliares`, `biblioteca` e `laboratorio`. Essa organização permite
investigar a relação entre os nomes dos diretórios e a orientação heurística.
Não se assume que um nome pouco similar exclua a presença de um alvo.

```sh
python3 gerar_arvore.py
```

O gerador não remove arquivos adicionais. Portanto, os números de referência
pressupõem exclusivamente os dados gerados, sem intervenções externas. O comando
informa a quantidade de pastas abaixo da raiz; os relatórios incluem a raiz em N.

### 3.2. Cenários de teste e documentos reais

A suíte cria e remove cenários próprios para verificar custos mínimos, empates,
correspondências entre blocos/páginas, ciclos simbólicos, ausência de objetivo,
erros de formato e instrumentação. As funções-oráculo enumeram objetivos ou leem
integralmente os dados para conferir resultados por uma estratégia independente.

O uso de uma pasta real deve registrar seu caminho, termos e formatos, mantendo
o destino dos resultados fora da raiz pesquisada. A avaliação do acervo fornecido
pelo usuário está em [VALIDACAO_DOCENCIA.md](VALIDACAO_DOCENCIA.md), com inventário,
conferência de custos e limitações de extração. Falhas de acesso ou PDF impedem
concluir a busca e são apresentadas explicitamente.

## 4. Definição operacional das métricas

| Métrica | Campo | Operacionalização |
| --- | --- | --- |
| Nós expandidos (N) | `pastas_abertas` | Incremento de uma unidade após listar cada diretório expandido. |
| Arquivos/Itens examinados | `itens_examinados` | Soma das entradas elegíveis das listagens: arquivos regulares e subdiretórios. |
| Correspondências descobertas | `arquivos_encontrados` | Arquivos que satisfazem o objetivo nas pastas expandidas; todos os arquivos no mapeamento. |
| Arquivos processados/lidos | `arquivos_lidos` | Conteúdos efetivamente lidos pela aplicação; zero em buscas por nome. |
| Custo do Caminho g(n) | `custo_g` | Soma dos custos locais no caminho raiz–pasta objetivo. |
| Consumo de Memória | `pico_mem_kb` | Pico dos blocos rastreados por tracemalloc, convertido para KiB. |
| Tempo de Execução | `tempo_ms` | Diferença de perf_counter durante a chamada de busca, em ms. |

`nos_expandidos` é um alias de `pastas_abertas`, sem contador adicional. No modo
nome, retorna-se o primeiro correspondente da pasta selecionada, embora outras
correspondências nessa pasta possam ser contabilizadas. UCS/A* também podem
descobrir candidaturas de outros ramos antes da seleção final. Assim, os
`encontrados` retornados e `arquivos_encontrados` têm significados distintos.

G utiliza itens na etapa 2 e bytes na etapa 3, incluindo raiz e pasta objetivo.
N, itens e leituras referem-se a toda a exploração até a parada. No mapeamento,
g não possui objetivo único; sem resultado, g=0 é convenção de armazenamento.
Essa convenção não transforma uma busca sem sucesso em exploração gratuita.
O f final de UCS/A* é `g+0`, pois se refere ao objetivo confirmado. Sem objetivo,
o relatório apresenta f como indefinido.

### 4.1. Escopo temporal

```text
tempo_ms = [perf_counter_fim − perf_counter_inicio] × 1000
```

O instrumento mede tempo decorrido, incluindo espera, e utiliza diferenças entre
leituras do contador, conforme a [documentação de perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter).
O intervalo inclui validação dos argumentos da busca, inicialização, listagem e
ordenação, manipulação da fronteira, correspondência, leitura/extração, contadores
e captura do rastro quando solicitada. Inclui espera por E/S e escalonamento.

Menu, seleção da função, importações, impressão, montagem dos registros, JSON,
Markdown e execução do perfil de memória ficam fora do intervalo. O tempo total
do comando é, portanto, maior que o valor de busca mostrado. A medida não isola
CPU nem duração exclusiva de operações físicas de disco.

### 4.2. Escopo de memória e unidades

```text
pico_mem_kb = tracemalloc.get_traced_memory()[1] / 1024
KB_decimal = pico_mem_kb × 1024 / 1000
```

Tracemalloc informa o pico dos blocos de memória rastreados
([documentação da função](https://docs.python.org/3/library/tracemalloc.html#tracemalloc.get_traced_memory)).
O perfil abrange alocações Python da chamada e do resultado, incluindo o rastro
solicitado. Ele não é RSS, memória total do processo ou tamanho do cache do
sistema. Estruturas já existentes antes do início do perfil não representam
novas alocações dessa chamada. A sessão é encerrada mesmo quando ocorre exceção.

O campo histórico `pico_mem_kb` armazena KiB, com divisor 1024. Os cabeçalhos
acadêmicos KB das etapas 1/2 recebem conversão decimal, com divisor 1000.
As métricas principais mantêm KiB. Não se comparam valores em unidades distintas
sem realizar essa conversão.

### 4.3. O significado das leituras

Um TXT é aberto e consumido até EOF uma vez por expansão, mesmo quando o termo
aparece no início. Arquivos vazios também contam como lidos. Todos os formatos
elegíveis da pasta são processados para determinar seu custo local integral.
No PDF, cada arquivo conta uma leitura, enquanto os bytes somam os dados
entregues ao parser, incluindo releituras após reposicionamento.

Esses contadores descrevem o trabalho da aplicação. O cache pode atender uma
leitura sem operação física no armazenamento. A medição de bytes do caminho
também não corresponde ao volume total de todos os ramos explorados.

## 5. Protocolo implementado

1. Definir etapa, raiz, termo, alfa e diretório externo para os resultados.
2. Preparar as chamadas dos algoritmos da etapa, sem listar antecipadamente a árvore.
3. Executar uma chamada temporizada de cada algoritmo, com tracemalloc desligado
   e estado novo, incluindo fronteira, visitados, métricas e rastro.
4. Repetir cada algoritmo em uma chamada exclusiva para memória, com nova sessão
   tracemalloc e novo estado, após concluir todos os tempos do lote.
5. Comparar caminhos, contadores e rastros de cada par de execuções.
6. Em caso de divergência ou erro de busca, interromper antes de montar registros
   de sucesso do lote. A comparação não substitui um snapshot do sistema de arquivos.
7. Associar o tempo da primeira chamada e o pico da segunda a contadores de uma
   execução, sem somar as duas buscas.
8. Montar registros, salvar JSONs e gerar as tabelas após concluir as medições.
9. Se desejado, exportar gráficos a partir dos JSONs. Importação e renderização
   de Matplotlib ficam fora das chamadas medidas e não iniciam novas buscas.

O protocolo utiliza **uma amostra temporal por algoritmo**, em ordem fixa, sem
limpeza do cache e sem tratamento estatístico automático. Não há repetições,
médias ou intervalos de confiança calculados pela interface. O campo
`protocolo_lote=tempos_antes_dos_perfis_memoria` identifica a ordem atual; sua
ausência em registros antigos não autoriza atribuir-lhes esse protocolo.

## 6. Reprodução das entregas

Execute a partir de `File-Hunter-Agent/`, usando um destino por experimento:

```sh
python3 gerar_arvore.py
python3 main.py --etapa 1 --resultados resultados/experimento/etapa1
python3 main.py --etapa 2 --alvo livro --alfa 100 --resultados resultados/experimento/etapa2
.venv/bin/python main.py --etapa 3 --alvo algoritmo --alfa 100 --resultados resultados/experimento/etapa3
```

Os comandos pressupõem o ambiente virtual com pypdf quando PDFs participarem.
A árvore padrão não contém PDFs e pode ser avaliada por conteúdo com o Python
do núcleo. As opções `--sem-salvar` e `--resultados` controlam a persistência.

| Entrega | Colunas e informações exigidas |
| --- | --- |
| Etapa 1 | Algoritmo; caminho completo relativo; ordem de descoberta; primeiros 10; total de pastas abertas; total de arquivos encontrados; tempo (ms); pico de memória (KB). |
| Etapa 2 | Algoritmo; alvo solicitado; caminho; pastas abertas; custo acumulado g(n); tempo (ms); memória (KB); decomposição dos custos do caminho. |
| Etapa 3 | Algoritmo; palavra no conteúdo; caminho; pastas abertas; arquivos lidos do disco; custo total f(n); tempo (ms); fórmula da heurística e diferença de N/leituras. |
| Complemento comum | Métricas principais com N, itens, arquivos processados/lidos, g, pico em KiB e tempo, além do percurso de expansões nas etapas. |

“Arquivos lidos do disco” é o cabeçalho solicitado para o contador da aplicação;
sua interpretação operacional é a da seção 4.3. A etapa 1 não lê conteúdos.
As buscas com objetivo podem expandir a árvore inteira se necessário, sem se
tornarem mapeamento global.

Os relatórios podem ser reconstruídos sem executar buscas:

```sh
python3 -m funcoes.relatorio resultados/experimento/etapa1 --etapa 1 --saida resultados/experimento/etapa1/reconstruido.md
python3 -m funcoes.relatorio resultados/experimento/etapa2 --etapa 2 --alvo livro --saida resultados/experimento/etapa2/reconstruido.md
python3 -m funcoes.relatorio resultados/experimento/etapa3 --etapa 3 --alvo algoritmo --saida resultados/experimento/etapa3/reconstruido.md
```

A leitura de diretórios de resultados não é recursiva. Experimentos e políticas
de leitura incompatíveis são separados. O esquema v1 aceita metadados opcionais
ausentes em registros antigos, apresentando informação não registrada quando
aplicável. A identificação do experimento agrupa amostras; não identifica sozinha
a revisão Git, que deve acompanhar a análise externa dos resultados.

## 7. Resultados de referência e interpretação

### 7.1. Mapeamento e busca por nome

No conjunto padrão, BFS e DFS do mapeamento abrem 41 pastas e encontram 64
arquivos, sem ler conteúdos. A ordem de descoberta difere a partir do quinto
arquivo. Esse resultado atende Q1: a cobertura coincide, mas a cronologia muda.

Na etapa 2, para `livro`, com alfa=100 no A*:

| Algoritmo | Pastas abertas | g do caminho (itens) |
| --- | ---: | ---: |
| BFS | 30 | 17 |
| DFS | 5 | 17 |
| UCS | 41 | 17 |
| A* | 30 | 17 |

Um caminho objetivo típico possui custos locais 4, 7, 1, 1 e 4, totalizando
17 itens. A comparação mostra que mesmo custo final não implica mesmo esforço
de exploração. A quantidade maior de expansões de UCS nesse conjunto não
contradiz sua seleção por custo acumulado.

### 7.2. Busca por conteúdo e contraexemplo

| Cenário | Termo / alfa do A* | N de UCS / A* | ΔN | Leituras de UCS / A* | ΔL | g de UCS / A* |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Árvore padrão | algoritmo / 100 | 41 / 41 | 0 | 52 / 52 | 0 | 320 / 320 bytes |
| Cenário controlado de pedagogia | pedagogia / 1000 | 3 / 2 | 1 | 2 / 1 | 1 | Mesmo custo para o mesmo arquivo. |
| Contraexemplo controlado | algoritmo / 1000 | 3 / 2 | 1 | 12 / 11 | 1 | 9 / 119 bytes |
| Acervo real Docencia/Fontes | algoritmo / 100 | 10 / 10 | 0 | 50 / 50 | 0 | 6.204.185 / 6.204.185 bytes |

Os dois cenários controlados estão em [test_astar.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_astar.py) e
podem ser reproduzidos com `python3 -m tests.test_astar` em cópias que contenham
a suíte local ou a revisão histórica indicada na seção 8. O cenário de pedagogia
utiliza um arquivo cujo nome não contém o termo, para caracterizar busca interna.

O primeiro caso não apresenta economia; o segundo apresenta economia; o terceiro
associa menos expansões a um caminho mais caro; o acervo real não apresenta
economia nesta configuração. Em conjunto, respondem Q2–Q4
sem atribuir superioridade universal à heurística. Tempos e picos de cada execução
estão nos JSONs e relatórios produzidos localmente; não são substituídos aqui
por uma média não calculada.

O relatório apresenta diferenças absolutas:

```text
ΔN = N_UCS − N_A*
ΔL = arquivos_lidos_UCS − arquivos_lidos_A*
```

Para bases UCS maiores que zero, as reduções percentuais são `100 × ΔN/N_UCS`
e `100 × ΔL/arquivos_lidos_UCS`. Com base zero, o percentual não se aplica;
preserva-se a diferença absoluta. No cenário de pedagogia, as reduções são
`100 × (3−2)/3 ≈ 33,33%` nas pastas e `100 × (2−1)/2 = 50%` nos arquivos lidos.
São resultados do cenário controlado, sem alteração de g ou do objetivo.

Valor positivo indica economia observada de A*; zero indica igualdade; negativo
indica trabalho adicional. A lista de pastas abertas por UCS e não por A*
descreve a execução. Ela não prova ausência de alvos nessas pastas nem constitui
uma poda fundamentada em admissibilidade da heurística.

O requisito de “demonstração de poda” é apresentado como trabalho evitado pela
priorização e parada antecipada. As leituras são aberturas e processamento real
pela aplicação, conforme a seção 4.3, sem inferir quantidade de operações físicas
no disco. A tabela usa contadores de uma execução por algoritmo; não soma as
execuções independentes de tempo e memória. A fórmula de h e seu cálculo numérico,
sem modelos de ML, estão na [seção 4.3 da arquitetura](ARQUITETURA.md#43-heurística-e-adaptação-de-a).

### 7.3. Avaliação com o acervo real

O acervo `../Docencia/Fontes` contém 62 PDFs e 11 diretórios, incluindo a raiz.
BFS/DFS cobriram todos os arquivos, com a primeira diferença de descoberta na
posição 23. Na busca por nome, UCS selecionou g=13 itens, contra 17 de BFS/DFS/A*.
Na busca por conteúdo, UCS/A* abriram 10 pastas, leram 50 PDFs e selecionaram
g=6.204.185 bytes, confirmado por uma agregação independente dos custos. Não houve
redução de expansões ou leituras por A* nesse parâmetro de alfa=100.

A auditoria separada processou 7.592 páginas e encontrou o termo no texto
extraído de 20 PDFs. Sete arquivos não forneceram texto, e o parser emitiu avisos
sobre suporte incompleto a determinadas fontes. A pesquisa visual desses arquivos
não foi validada. Tempos, picos de memória, arquivos afetados, ambiente e artefatos
estão descritos no [relatório da validação](VALIDACAO_DOCENCIA.md). Esses dados
complementam os cenários controlados, sem substituir suas condições ou presumir
o comportamento de outros acervos.

### 7.4. Verificação da revisão de código

Antes da unificação do percurso BFS/DFS, foram preservados os resultados de oito
execuções: duas estratégias em quatro tarefas (mapeamento, nome `livro`, conteúdo
`algoritmo` e nome ausente). O cenário usa o gerador de seed 2024 e acrescenta
um diretório com 1.024 subpastas vazias. A repetição após a mudança conferiu
igualdade integral dos caminhos, de todos os contadores e dos rastros de expansão.

A memória foi comparada separadamente apenas no mapeamento desse diretório largo:

| Estratégia | Pastas abertas | Pico antes (KiB) | Pico depois (KiB) | Diferença (KiB) |
| --- | ---: | ---: | ---: | ---: |
| BFS | 1.025 | 509,127 | 500,631 | 8,496 |
| DFS | 1.025 | 509,127 | 500,631 | 8,496 |

A redução foi de aproximadamente 1,67% nessa amostra. Corresponde à eliminação
da lista auxiliar de subpastas, com ajustes constantes do motor compartilhado.
Cada versão foi medida uma vez por estratégia com tracemalloc, no Python 3.9.6
do mesmo ambiente; não foi realizado um benchmark comparativo de tempo nem se
afirma redução em outras árvores. Artefatos locais: `resultados/revisao_final/antes.json`
e `resultados/revisao_final/depois.json`.
Esses são os caminhos originais dos registros; após a reorganização, seu conteúdo
foi preservado no arquivo externo indicado na [validação do acervo](VALIDACAO_DOCENCIA.md#6-artefatos-e-reprodução).
O cenário temporário foi removido após a conferência; os registros e relatórios
foram preservados. Sua preparação consiste em executar o gerador em uma raiz
isolada e acrescentar o diretório `fronteira_larga` com as subpastas vazias.

Também foi reproduzido e corrigido um erro de validação: alvos não textuais
podiam gerar AttributeError ao executar casefold, e A* preparava a heurística
antes de rejeitar `None`. Os testes agora exigem ValueError para alvos vazios ou
de tipo inválido nas quatro estratégias, em ambos os modos; uma raiz inexistente
confirma que essa falha é apresentada antes de tentar expandir a árvore.
O caso A* é conferido com alfa zero e positivo.

As chamadas públicas e o esquema JSON foram preservados. As medições históricas
do acervo real permanecem resultados da revisão identificada em
[VALIDACAO_DOCENCIA.md](VALIDACAO_DOCENCIA.md); não foram reatribuídas à refatoração.

## 8. Verificação e rastreabilidade dos requisitos

Por decisão de organização da entrega, `tests/` é mantido apenas localmente e
ignorado pelo Git. Um clone da revisão atual contém o programa e a documentação,
sem essa pasta. A suíte que sustenta as verificações abaixo está preservada na
[revisão 5a985d3](https://github.com/samuelcotinguiba/File-Hunter-Agent/tree/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests).
Os links da tabela apontam para essa revisão, mantendo a rastreabilidade sem
incluir os arquivos na entrega atual.

| Propriedade verificada | Evidência na suíte |
| --- | --- |
| FIFO/LIFO, descoberta e primeiro objetivo | [test_buscas.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_buscas.py). |
| g mínimo de UCS, empates e custos concorrentes | [test_ucs.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_ucs.py), com enumeração independente dos objetivos. |
| Conteúdo, bytes, binários e leitura integral | [test_conteudo.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_conteudo.py). |
| Unicode, termos entre blocos e memória da leitura | [test_revisao.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_revisao.py). |
| Alvo textual não vazio antes de acessar a árvore | [test_revisao.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_revisao.py), nas quatro estratégias e dois modos, incluindo A* com alfa zero/positivo. |
| Jaccard, alfa zero, economia e contraexemplo | [test_astar.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_astar.py). |
| JSON, colisões, validação e apresentação | [test_relatorio.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_relatorio.py). |
| Subpastas e cobertura de formatos | [test_formatos.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_formatos.py), [test_pdf.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_pdf.py). |
| Colunas e grupos do comparativo | [test_comparacao.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_comparacao.py). |
| Contadores, instrumentos e unidades | [test_metricas.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_metricas.py). |
| Escopo por etapa, cronologias, rastros e duplicatas | [test_etapas.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_etapas.py). |
| Tempo isolado do perfil e dos registros | [test_timer.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_timer.py), com relógio controlado. |
| Seleção e preferência fora das buscas | [test_pastas.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_pastas.py): restauração, cancelamento, falhas/colisões de JSON, navegação sem conteúdos e adaptadores gráficos simulados. |
| Visualização opcional e representação das métricas | [test_visualizacao.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_visualizacao.py): ausência do extra, menu/CLI, grupos distintos, valores/unidades, custo ausente, PNGs, colisão e falha de gravação. |
| Continuidade das entregas na sessão | [test_interface.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_interface.py): três etapas sequenciais, retorno, termos/pasta, gráficos sem nova busca, resumo com artefatos completos, alfa e recuperação de erros. |
| Dispensa de descendentes de objetivo | [test_otimizacao.py](https://github.com/samuelcotinguiba/File-Hunter-Agent/blob/5a985d3e73cbdcc00620f12b22118f98a68ef449/tests/test_otimizacao.py), com custos e consultas verificáveis. |

```sh
python3 -m tests
.venv/bin/python -m tests
```

Esses comandos aplicam-se à cópia local que mantém `tests/` ou à revisão
histórica, não a um clone da entrega atual sem a suíte.

A primeira execução sinaliza a ausência do extrator se pypdf não estiver
instalado; a segunda, no ambiente preparado, inclui PDFs reais, comprimidos,
protegidos, sem texto e fronteiras entre páginas. O teste do timer mantém
125 ms de busca enquanto simula 1000 s no perfil e 500 s na criação do registro:
esses intervalos simulados não devem integrar o tempo apresentado.
Com o extra de gráficos, a suíte inclui renderização real pelo Agg; sem ele,
confere o fluxo opcional e informa que essa renderização não foi executada.
Um processo novo confirma que importar a interface e executar uma etapa não
carrega Matplotlib. Os gráficos representam uma amostra por algoritmo, sem
repetições estatísticas, normalização entre unidades ou alegação de superioridade.
O teste do timer também atribui 250 s simulados a cada aviso de progresso e mantém
125 ms por busca; os avisos ocorrem com tracemalloc desligado. A navegação entre
etapas, o resumo, a pergunta de retorno e os gráficos não integram as medições.
O resumo interativo omite listas longas, mas os artefatos e a opção de relatório
completo preservam a cronologia integral e os percursos exigidos.

Matplotlib pode instalar fontTools como dependência transitiva. Comparações de
PDF devem registrar essa configuração externamente: o esquema atual identifica
pypdf, mas não a versão de fontTools. Os resultados históricos do acervo foram
obtidos sem esse extra e permanecem vinculados ao ambiente registrado.

Os testes de seleção simulam os diálogos nativos, sem abrir janelas durante a
suíte. O AppleScript foi compilado pelo compilador do macOS; a interação visual
com o diálogo permanece uma verificação manual no desktop. Navegação, gravação
e restauração da pasta são verificadas também pela interface, sem incluir esse
trabalho nas métricas dos algoritmos. A CLI direta mantém a raiz didática quando
não recebe `--raiz` nem flag de seleção, independentemente do último caminho salvo.

Verificar a suíte não equivale a obter cobertura de testes de 100% ou demonstrar
ausência de defeitos. A avaliação também não substitui a execução sobre a pasta
real que será utilizada na apresentação.

## 9. Ameaças à validade e limites de generalização

| Dimensão | Limitação e consequência |
| --- | --- |
| Validade interna | Ordem fixa e cache favorecem potencialmente algoritmos posteriores; uma amostra não separa efeito do algoritmo de variações ambientais. |
| Instrumentação | Tempo e memória vêm de chamadas distintas; diferenças observáveis são detectadas, mas não há snapshot da árvore. |
| Validade de construto | g mede um caminho; leituras medem arquivos da aplicação; tracemalloc mede alocações rastreadas. Essas variáveis não equivalem a custo total de E/S, operações físicas ou RSS. |
| Validade externa | A árvore sintética é pequena e controlada; outros formatos, tamanhos, profundidades e distribuições podem produzir resultados diferentes. |
| Heurística | Jaccard lexical não estima um limite inferior demonstrado; o efeito depende dos nomes e do peso na unidade de custo. |
| Sistema de arquivos | Verificações de symlinks não impedem alterações concorrentes entre validação e abertura; diretórios inacessíveis interrompem a busca. |
| Formatos | Classificação textual por extensão e UTF-8 com descarte de erros não substituem detecção de codificação; PDF possui limitações de extração e não inclui OCR. |
| Persistência | Criação exclusiva protege cada JSON contra sobrescrita, mas não fornece transação atômica do lote em falha de gravação ou queda abrupta. |

Uma avaliação estatística ampliada poderia controlar ou variar a ordem, executar
repetições, caracterizar o equipamento e apresentar medidas de dispersão. Esses
procedimentos são possibilidades de extensão, não funcionalidades já implementadas.
A análise atual utiliza observações por cenário e os invariantes de correção.

## 10. Referências e orientação para o relatório

1. PYTHON SOFTWARE FOUNDATION. [time — perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter). Documentação oficial.
2. PYTHON SOFTWARE FOUNDATION. [tracemalloc — get_traced_memory](https://docs.python.org/3/library/tracemalloc.html#tracemalloc.get_traced_memory). Documentação oficial.
3. FILE HUNTER AGENT. [Arquitetura e modelo computacional](ARQUITETURA.md), [código das métricas](../funcoes/metricas.py) e [histórico de implementação](HISTORICO.md). Fontes internas do experimento.

Na redação acadêmica, apresentar problema e objetivos, modelo computacional,
metodologia, resultados, discussão e limitações. Identificar raiz, termos, alfa,
versões do ambiente e revisão Git, vinculando as tabelas aos JSONs do experimento.
Conclusões devem distinguir menor custo de caminho, menor exploração e menor
tempo observado: essas propriedades não são intercambiáveis.
