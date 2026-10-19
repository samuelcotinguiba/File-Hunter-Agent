# File Hunter Agent

Projeto acadêmico em Python que compara **BFS, DFS, UCS e A*** na exploração de
diretórios e na localização de arquivos por nome ou conteúdo. Cada diretório é
um nó do espaço de busca; sua expansão lista o conteúdo com `os.scandir`, sem
seguir links simbólicos.

Este README reúne a visão geral e os comandos iniciais. A descrição completa
do projeto está na **[pasta docs/](docs/)**, acessível diretamente pelo GitHub.

## O que o projeto entrega

| Etapa | Estratégias | Objetivo |
| --- | --- | --- |
| 1 | BFS e DFS | Mapear todos os arquivos e comparar a ordem de descoberta. |
| 2 | BFS, DFS, UCS e A* | Localizar o primeiro alvo no nome; g(n) soma itens no caminho. |
| 3 | UCS e A* | Localizar uma palavra no conteúdo; g(n) soma bytes lidos no caminho. |

O mapeamento completo pertence à etapa 1. As buscas com alvo encerram quando
confirmam a pasta do resultado e podem explorar toda a árvore se necessário.
As tabelas comparam caminhos, expansões, itens examinados, leituras, custos,
tempo e memória. A etapa 1 registra também os primeiros dez arquivos; a etapa 3
apresenta a heurística e a diferença de expansões e leituras entre UCS e A*.

## Execução rápida

Execute a partir da pasta `File-Hunter-Agent/`:

```sh
python3 gerar_arvore.py
python3 -m tests
python3 main.py
```

O último comando abre o menu interativo. Para executar as entregas diretamente
sobre a árvore didática, sem gravar relatórios:

```sh
python3 main.py --etapa 1 --sem-salvar
python3 main.py --etapa 2 --alvo livro --alfa 100 --sem-salvar
python3 main.py --etapa 3 --alvo algoritmo --alfa 100 --sem-salvar
```

O núcleo utiliza a biblioteca padrão. A leitura de conteúdo PDF usa **pypdf**,
dependência externa opcional fixada em [requirements.txt](requirements.txt).
Para habilitá-la, prepare o ambiente e execute com seu interpretador:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m tests
.venv/bin/python main.py
```

Ambiente verificado: Python 3.9.6; a extensão PDF requer Python 3.9+.
Os exemplos de ambiente virtual usam caminhos POSIX. Os testes sem pypdf
sinalizam a ausência do extrator; os testes na `.venv` preparada incluem PDFs.

## Seleção da pasta de busca

No menu, **8** abre a seleção de pastas e **9** permite navegar no terminal.
O seletor do sistema também pode ser chamado diretamente:

```sh
python3 main.py --selecionar-pasta
python3 main.py --navegar --raiz ../Docencia/Fontes
python3 main.py --raiz ../Docencia/Fontes
```

O menu restaura a última pasta válida, salva em `.file_hunter.json` local,
ignorado pelo Git. `--config` muda esse arquivo e `--raiz` prevalece sobre ele.
Comandos diretos com `--etapa`/`--algoritmo`, sem seleção interativa e sem `--raiz`,
mantêm `./docencia/fontes` como padrão reproduzível. Caminhos relativos usam o
diretório de trabalho atual. No ambiente de validação, o acervo real está em
`../Docencia/Fontes`; em outro computador, selecione a pasta correspondente.
Detalhes e exemplos estão no [guia de uso](docs/USO.md#2-como-a-pasta-é-escolhida).

## Estruturas de dados e justificativas de design

| Escolha | Finalidade |
| --- | --- |
| `collections.deque` | BFS com `popleft()` e DFS com `pop()`. |
| `heapq` | UCS/A* com `(prioridade, contador, nó)` e desempate estável. |
| `set` de realpaths | Controle de visitados, com exclusão de symlinks. |
| Motores compartilhados | Mesmas regras de expansão e contagem para estratégias comparáveis. |
| Leitura em blocos e adaptador PDF | Conteúdo textual com memória limitada; formato PDF isolado. |
| JSON validado | Reconstrução de tabelas sem repetir buscas. |

A* usa `h(n) = alfa × (1 − Jaccard dos bigramas)` e `f(n) = g(n) + h(n)`.
A heurística não é admissível; economia de leituras e caminho ótimo não são
garantidos. Custos locais são conhecidos durante a expansão, sem listagens
antecipadas gratuitas. [Justificativas completas](docs/ARQUITETURA.md).

## Métricas e execução

N mede diretórios abertos; itens incluem arquivos e subpastas listados; arquivos
lidos contam conteúdos processados pela aplicação. g soma custos no caminho da
raiz ao objetivo. Tempo usa `time.perf_counter` em ms; memória usa o pico de
alocações Python de `tracemalloc` em KiB, em uma execução separada.

O processamento é **síncrono e sequencial**. Python não torna essas leituras
assíncronas automaticamente. Preservamos a ordem dos algoritmos e medimos cada
um isoladamente. O [protocolo experimental](docs/METODOLOGIA.md) detalha as
medições e suas limitações.

## Resultados e limites

`resultados/` é criado ao salvar uma execução e fica ignorado pelo Git.
`--sem-salvar` evita gravar resultados; `--resultados` define outro destino.
Os relatórios são gerados em JSON e Markdown. O salvamento da última pasta é
uma preferência independente dessas saídas.

A busca pelo nome aceita qualquer extensão. Conteúdo considera textos e PDFs
com texto extraível; Office e OCR não estão implementados. fontTools está
documentado como melhoria futura. No acervo real, UCS e A* abriram 10 pastas e
leram 50 PDFs cada para `algoritmo`: não houve redução nessa configuração.
A [validação](docs/VALIDACAO_DOCENCIA.md) e a [metodologia](docs/METODOLOGIA.md)
explicam os resultados, os casos de economia e as limitações de extração.

## Organização do projeto

```text
File-Hunter-Agent/
├── README.md               # resumo e entrada da documentação
├── main.py                 # menu, CLI e coordenação
├── gerar_arvore.py          # dados didáticos reproduzíveis
├── requirements.txt        # extra opcional de PDF
├── funcoes/                # buscas, acesso, métricas e relatórios
├── tests/                  # cenários e regressões
└── docs/                   # documentação detalhada
    ├── AGENTS.md           # contratos de manutenção e decisões de design
    ├── ARQUITETURA.md      # módulos, estruturas e justificativas
    ├── DESENVOLVIMENTO.md  # objetivos e construção por etapas
    ├── HISTORICO.md        # mudanças e verificações por entrega
    ├── METODOLOGIA.md      # métricas e protocolo experimental
    ├── USO.md              # instalação, seleção de pastas e comandos
    └── VALIDACAO_DOCENCIA.md # experimentos com o acervo real
```

A árvore didática `docencia/fontes/` é um dado local gerado, ignorado pelo Git.

## Documentação completa

Consulte os documentos abaixo ou abra a **[pasta docs/ no GitHub](docs/)**.

| Documento | Conteúdo |
| --- | --- |
| [Guia de uso](docs/USO.md) | Ambiente, seleção de pastas, etapas e geração de relatórios. |
| [Arquitetura](docs/ARQUITETURA.md) | Modelo de busca, módulos, estruturas, custos e justificativas das escolhas. |
| [Metodologia](docs/METODOLOGIA.md) | Definições das métricas, protocolo, testes e interpretação dos resultados. |
| [Validação com Docencia/Fontes](docs/VALIDACAO_DOCENCIA.md) | Experimentos com PDFs reais e limitações da extração de texto. |
| [Desenvolvimento](docs/DESENVOLVIMENTO.md) | Objetivos, construção por etapas e estado funcional da entrega. |
| [Histórico](docs/HISTORICO.md) | Registro das alterações, decisões e verificações realizadas. |
| [Contratos de manutenção — AGENTS.md](docs/AGENTS.md) | Regras técnicas e decisões de design para manter o projeto. |
