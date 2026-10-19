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

Com o ambiente preparado, execute na pasta `File-Hunter-Agent/`:

```sh
.venv/bin/python main.py
```

O menu apresenta as **três etapas do professor**. Escolha uma etapa; o programa
seleciona os algoritmos da comparação e pede apenas a palavra necessária.
A pasta é reaproveitada entre execuções. Ao terminar, ele pergunta se deseja
voltar ao menu: **Enter/S** retorna, **N** encerra e **P** segue para a próxima
etapa. **G** gera o gráfico do resultado atual e **R** mostra o relatório completo.
O resumo exibe tabelas alinhadas e caminhos separados; as ações para continuar
ficam em um bloco próprio, com espaço após os resultados.

Buscas individuais, gráficos antigos e ajustes da heurística ficam em
**5 — Mais opções**. A CLI continua disponível para automatizar as entregas.

O núcleo utiliza a biblioteca padrão. A instalação completa reúne **pypdf**
(conteúdo PDF) e **Matplotlib** (gráficos) em um único
[requirements.txt](requirements.txt). Na primeira utilização, prepare o ambiente:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Depois, use apenas o comando inicial. `gerar_arvore.py` cria dados didáticos
opcionais; os testes são executados com `.venv/bin/python -m tests`.
O [guia de uso](docs/USO.md) reúne os comandos de cada etapa e a seleção do acervo.

Ambiente verificado: Python 3.9.6; os extras PDF e gráficos requerem Python 3.9+.
Os exemplos de ambiente virtual usam caminhos POSIX. Os testes sem pypdf
sinalizam a ausência do extrator; os testes na `.venv` preparada incluem PDFs.

## Gráficos opcionais com Matplotlib

A ação **G**, após uma comparação, exporta o gráfico em PNG e informa que requer
**Matplotlib**, instalado pelo `requirements.txt`. O uso do recurso é opcional.
O resultado atual é reutilizado diretamente, inclusive com `--sem-salvar`.
Para gráficos de JSONs existentes, use **5 — Mais opções → 2** ou a CLI:

```sh
.venv/bin/python main.py --etapa 2 --alvo livro --resultados resultados/etapa2
.venv/bin/python main.py --graficos resultados/etapa2 --saida-graficos resultados/graficos
```

Os gráficos reutilizam os registros medidos, sem repetir buscas, e apresentam seis métricas
em painéis separados. Cada experimento/política gera seu próprio PNG, sem exigir
janela gráfica. [Uso e dependências transitivas](docs/USO.md#8-gráficos-opcionais-com-matplotlib).

## Seleção da pasta de busca

No menu, **4 — Escolher outra pasta** oferece seletor do sistema, navegação no
terminal e digitação do caminho. A última pasta válida é restaurada ao iniciar.
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
com texto extraível; Office e OCR não estão implementados. O extra de gráficos
instala também fontTools; seu efeito na extração dos PDFs ainda requer validação
específica. No acervo real, UCS e A* abriram 10 pastas e
leram 50 PDFs cada para `algoritmo`: não houve redução nessa configuração.
A [validação](docs/VALIDACAO_DOCENCIA.md) e a [metodologia](docs/METODOLOGIA.md)
explicam os resultados, os casos de economia e as limitações de extração.

## Organização do projeto

```text
File-Hunter-Agent/
├── README.md               # resumo e entrada da documentação
├── main.py                 # argumentos, APIs e coordenação das medições
├── gerar_arvore.py          # dados didáticos reproduzíveis
├── requirements.txt        # dependências de PDF e gráficos
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
