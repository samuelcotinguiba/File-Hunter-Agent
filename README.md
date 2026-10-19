# File Hunter Agent

Projeto acadêmico em Python para comparar BFS, DFS, UCS e A* na exploração de
pastas e localização de arquivos por nome ou conteúdo. Um nó é um diretório;
expandir significa listar seu conteúdo com `os.scandir`, sem seguir symlinks.

**A documentação completa está em [docs/](docs/README.md)**: uso, arquitetura,
método experimental, validação com PDFs, desenvolvimento e histórico.

## O que o projeto entrega

| Etapa | Estratégias | Objetivo |
| --- | --- | --- |
| 1 | BFS e DFS | Mapear todos os arquivos e comparar a ordem de descoberta. |
| 2 | BFS, DFS, UCS e A* | Encontrar uma palavra no nome, com g acumulado em itens. |
| 3 | UCS e A* | Encontrar uma palavra no conteúdo, com g acumulado em bytes lidos. |

As entregas incluem caminhos, pastas abertas, itens examinados, arquivos lidos,
custo do caminho, tempo e memória. Na etapa 1, incluem a cronologia e os primeiros
10 arquivos; na etapa 3, a fórmula da heurística e a diferença de expansões/leituras.

## Execução rápida

Execute a partir da pasta `File-Hunter-Agent/`:

```sh
python3 gerar_arvore.py
python3 -m tests
python3 main.py --etapa 1 --sem-salvar
python3 main.py --etapa 2 --alvo livro --alfa 100 --sem-salvar
python3 main.py --etapa 3 --alvo algoritmo --alfa 100 --sem-salvar
```

Sem `--etapa` ou `--algoritmo`, `python3 main.py` oferece o menu.
O núcleo utiliza a biblioteca padrão. PDFs com texto extraível usam **pypdf**,
dependência externa opcional fixada em `requirements.txt`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m tests
```

Ambiente verificado: Python 3.9.6; a extensão PDF requer Python 3.9+.
Os exemplos de ambiente virtual usam caminhos POSIX. Os testes sem pypdf
sinalizam a ausência do extrator; os testes na `.venv` preparada incluem PDFs.

## Como escolher a pasta Docencia

`--raiz` define a pasta inicial e todas as buscas consideram suas subpastas.
Sem esse argumento, usa-se `./docencia/fontes`, a árvore didática do gerador.
O acervo real fica fora do projeto, em `../Docencia/Fontes`:

```sh
python3 main.py --raiz ../Docencia/Fontes
.venv/bin/python main.py --raiz ../Docencia/Fontes --etapa 3 --alvo algoritmo --alfa 100
```

O primeiro comando abre o menu usando o acervo real. Caminhos relativos usam
o diretório de trabalho atual; não há escolha automática de pasta.
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
um isoladamente. [Protocolo e limitações](docs/METODOLOGIA.md) ·
[Justificativa da execução síncrona](docs/ARQUITETURA.md#61-execução-síncrona-e-possível-concorrência).

## Resultados e limites

`resultados/` é criado ao salvar uma execução e fica ignorado pelo Git.
`--sem-salvar` evita a gravação; `--resultados` define outro destino.
Os artefatos antigos foram arquivados fora do projeto. O código de geração de
JSON e Markdown continua disponível para as entregas exigidas.

A busca pelo nome aceita qualquer extensão. Conteúdo considera textos e PDFs
com texto extraível; Office e OCR não estão implementados. fontTools está
documentado como melhoria futura. No acervo real, UCS e A* abriram 10 pastas e
leram 50 PDFs cada para `algoritmo`: não houve redução nessa configuração.
A [validação](docs/VALIDACAO_DOCENCIA.md) e a [metodologia](docs/METODOLOGIA.md)
explicam os resultados, os casos de economia e as limitações de extração.

## Organização

```text
File-Hunter-Agent/
├── AGENTS.md               # contratos de manutenção
├── README.md               # resumo e entrada da documentação
├── main.py                 # menu, CLI e coordenação
├── gerar_arvore.py          # dados didáticos reproduzíveis
├── requirements.txt        # extra opcional de PDF
├── funcoes/                # buscas, acesso, métricas e relatórios
├── tests/                  # cenários e regressões
└── docs/                   # documentação detalhada e histórico
```

A árvore didática `docencia/fontes/` é um dado local gerado, ignorado pelo Git.
A evolução do projeto está em [docs/HISTORICO.md](docs/HISTORICO.md); o processo
de construção está em [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md).
