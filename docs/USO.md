# Guia de uso e organização dos dados

[Índice da documentação](README.md) · [Resumo do projeto](../README.md)

## 1. Ambiente e preparação

Execute a partir da pasta `File-Hunter-Agent/`. O ambiente verificado é Python
3.9.6; o núcleo usa recursos disponíveis a partir do Python 3.7, sem afirmar uma
matriz de testes de todas as versões. A dependência PDF fixada exige Python 3.9+.
O núcleo usa a biblioteca padrão, incluindo dataclasses. pypdf é uma biblioteca
externa opcional, autorizada para extração de conteúdo PDF.

```sh
python3 -m tests
python3 main.py --help
```

Para habilitar PDFs com texto extraível:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m tests
```

Os exemplos de ambiente virtual usam caminhos POSIX. A suíte com `python3`
sinaliza a ausência do extrator quando pypdf não está instalado; o Python da
`.venv` preparada verifica também o extrator. Não usar `-O` nos testes, pois
removeria as asserções.

## 2. Como a pasta é escolhida

A opção `--raiz` informa o diretório inicial. Ela vale para etapas e buscas
individuais, inclusive quando a escolha do algoritmo é feita pelo menu.
Caminhos relativos são resolvidos a partir do diretório de trabalho atual;
não há detecção automática do acervo nem escolha de pasta no menu.

| Situação, executando da pasta do projeto | Raiz utilizada |
| --- | --- |
| Sem `--raiz` | `./docencia/fontes`, árvore didática gerada localmente. |
| `--raiz ../Docencia/Fontes` | Acervo real localizado ao lado da pasta do projeto. |
| `--raiz "/caminho/com espaços/documentos"` | Pasta explicitamente informada. |

```sh
python3 main.py --raiz ../Docencia/Fontes
python3 main.py --raiz ../Docencia/Fontes --algoritmo bfs --modo nome --alvo livro --sem-salvar
```

Esses comandos usam o acervo real. O primeiro abre o menu com essa raiz; o
segundo executa uma busca pelo nome. As subpastas são percorridas conforme a
estratégia, sem seguir symlinks. Apenas BFS/DFS no mapeamento da etapa 1 esgotam
obrigatoriamente a árvore; buscas com objetivo podem encerrar antes.

A pasta de entrada e o destino dos resultados devem ser distintos. O programa
consulta os arquivos de entrada; JSONs e relatórios são gravados no destino de
saída. A árvore deve permanecer estática durante as medições.

## 3. Dados didáticos reproduzíveis

```sh
python3 gerar_arvore.py
```

O gerador cria `./docencia/fontes/` com seed 2024: 40 diretórios abaixo da raiz,
profundidade máxima de quatro níveis e 64 arquivos `.txt`, `.md`, `.py` e `.png`.
Incluindo a raiz, o mapeamento abre 41 pastas. A reexecução sobrescreve seus
arquivos conhecidos e preserva arquivos adicionais; os números de referência
pressupõem uma árvore sem alterações externas. O gerador não utiliza o acervo
real `../Docencia/Fontes` como destino.

## 4. Menu e buscas individuais

```sh
python3 main.py
```

As opções 1 a 4 executam BFS, DFS, UCS e A*. As opções 5, 6 e 7 executam as
etapas 1, 2 e 3. A opção 0 encerra. Nas buscas individuais, o menu solicita
modo e termo quando não foram definidos por argumentos; a raiz vem de `--raiz`
ou do padrão descrito na seção 2.

```sh
python3 main.py --raiz ./docencia/fontes --algoritmo bfs --modo nome --alvo .png --sem-salvar
.venv/bin/python main.py --raiz ../Docencia/Fontes --algoritmo astar --modo conteudo --alvo algoritmo --alfa 100
```

A correspondência usa substring após casefold, sem diferenciar maiúsculas.
Não há glob ou expressão regular: `.pdf` também pode ocorrer no meio do nome.
Busca por nome aceita qualquer arquivo regular, inclusive PDF, Office, imagens
ou arquivos sem extensão, sem abrir seu conteúdo. Por nome retorna-se o primeiro
arquivo da pasta objetivo selecionada; por conteúdo, os correspondentes dessa pasta.

Conteúdo usa as extensões de texto declaradas em [conteudo.py](../funcoes/conteudo.py)
e PDF com pypdf. Conteúdo Office, arquivos compactados e OCR não são suportados.
PDFs sem camada textual podem não fornecer palavras pesquisáveis. A distinção
entre suporte a fontes e OCR está na [arquitetura](ARQUITETURA.md#51-possível-uso-futuro-de-fonttools).

## 5. Entregas por etapa

| Etapa | Algoritmos | Alvo padrão | Entrega |
| --- | --- | --- | --- |
| 1: mapeamento global | BFS/DFS | Sem alvo | Todos os caminhos, cronologia e primeiros 10, totais, tempo e memória. |
| 2: busca por nome | BFS/DFS/UCS/A* | livro | Primeiro caminho, N, g, tempo, memória e decomposição do custo. |
| 3: busca por conteúdo | UCS/A* | algoritmo | Caminho, N, arquivos lidos, f final, tempo, memória e diferenças de expansão/leitura. |

```sh
python3 main.py --etapa 1 --resultados resultados/entregas/etapa1
python3 main.py --etapa 2 --alvo livro --alfa 100 --resultados resultados/entregas/etapa2
.venv/bin/python main.py --etapa 3 --alvo algoritmo --alfa 100 --resultados resultados/entregas/etapa3
```

Esses exemplos usam a árvore didática padrão. Para o acervo real:

```sh
.venv/bin/python main.py --etapa 3 --raiz ../Docencia/Fontes --alvo algoritmo --alfa 100 --resultados resultados/docencia/etapa3
```

`--comparar` equivale à etapa 3. Alfa padrão é 1; o valor 100 é um parâmetro dos
experimentos de referência, não uma garantia de melhor desempenho. A etapa define
algoritmos e modo e rejeita opções incompatíveis. Etapa 1 não recebe alvo nem alfa.

## 6. Resultados, persistência e relatórios

A pasta `resultados/` contém saídas de execução e não integra o código ou a
documentação versionada. Não precisa existir antes da primeira gravação:
`salvar_registro` e `salvar_markdown` criam o destino quando necessário.
`--sem-salvar` desativa a persistência e `--resultados` seleciona outro destino.

Cada etapa salva JSONs exclusivos e atualiza `etapa_N.md`. O esquema v1 registra
parâmetros, caminhos, métricas, configuração de conteúdo e método de medição.
As etapas acrescentam experimento, rastro de expansões e, no mapeamento,
`primeiros_10`. Campos opcionais preservam compatibilidade com registros antigos.

O conversor valida JSONs e reconstrói Markdown sem executar buscas:

```sh
python3 -m funcoes.relatorio resultados/entregas/etapa1 --etapa 1 --saida resultados/entregas/etapa1/reconstruido.md
python3 -m funcoes.relatorio resultados/entregas/etapa2 --etapa 2 --alvo livro --saida resultados/entregas/etapa2/reconstruido.md
python3 -m funcoes.relatorio resultados/entregas/etapa3 --etapa 3 --alvo algoritmo --saida resultados/entregas/etapa3/reconstruido.md
```

`--comparativo` seleciona somente UCS/A* por conteúdo; `--alvo` muda o termo.
Sem essas opções ou `--etapa`, gera-se o relatório geral. A leitura de diretórios
de JSONs não é recursiva. Registros incompatíveis ficam em grupos separados;
comparações do mapeamento exigem um JSON por algoritmo/experimento. Erros de
formato incluem o caminho do arquivo.

## 7. Processamento síncrono

As funções de busca executam sequencialmente. `os.scandir`, a leitura dos textos
e a extração PDF são chamadas síncronas. Python não as converte automaticamente
em operações assíncronas. Os algoritmos de uma etapa também são medidos um após
o outro: todos os tempos primeiro, depois os perfis de memória.

Essa escolha conserva a ordem da fronteira, a parada no objetivo e a atribuição
das métricas a cada execução. Assincronia poderia ser avaliada em outra versão,
por exemplo para manter uma interface responsiva, com trabalho explícito de
coordenação e novos testes. Não foi implementada nem teve ganho de desempenho
medido neste projeto. A justificativa está na [seção 6.1 da arquitetura](ARQUITETURA.md#61-execução-síncrona-e-possível-concorrência).
