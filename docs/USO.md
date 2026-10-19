# Guia de uso e organização dos dados

[Pasta de documentação](./) · [Resumo do projeto](../README.md)

## 1. Ambiente e preparação

Execute a partir da pasta `File-Hunter-Agent/`. O ambiente verificado é Python
3.9.6; o núcleo usa recursos disponíveis a partir do Python 3.7, sem afirmar uma
matriz de testes de todas as versões. A dependência PDF fixada exige Python 3.9+.
O núcleo usa a biblioteca padrão, incluindo dataclasses. pypdf é uma biblioteca
externa opcional, autorizada para extração de conteúdo PDF.
Matplotlib é exclusivo dos gráficos descritos na seção 8. Ambas as dependências
estão reunidas no único `requirements.txt`; seu uso permanece opcional no código.

```sh
python3 -m tests
python3 main.py --help
```

Para instalar o suporte a PDFs com texto extraível e aos gráficos:

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

A pasta pode ser escolhida no seletor nativo, na navegação do terminal ou por
`--raiz`. O menu mostra a pasta atual; a opção 8 oferece seleção pelo sistema,
navegação ou digitação de caminho, e a opção 9 abre diretamente a navegação.
Caminhos relativos usam o diretório de trabalho atual.

| Situação, executando da pasta do projeto | Raiz utilizada |
| --- | --- |
| Menu ou seletor sem `--raiz` | Última pasta válida do JSON; na ausência dela, `./docencia/fontes`. |
| CLI direta com etapa/algoritmo, sem seletor e sem `--raiz` | `./docencia/fontes`, sem depender de preferências anteriores. |
| `--raiz ../Docencia/Fontes` | Acervo real localizado ao lado da pasta do projeto. |
| `--raiz "/caminho/com espaços/documentos"` | Pasta explicitamente informada. |

```sh
python3 main.py --selecionar-pasta
python3 main.py --navegar --raiz ../Docencia/Fontes
python3 main.py --raiz ../Docencia/Fontes
python3 main.py --raiz ../Docencia/Fontes --algoritmo bfs --modo nome --alvo livro --sem-salvar
```

Os exemplos com `--raiz ../Docencia/Fontes` usam o acervo real. O seletor permite
escolher outro diretório; o último comando executa uma busca pelo nome.
As subpastas são percorridas conforme a
estratégia, sem seguir symlinks. Apenas BFS/DFS no mapeamento da etapa 1 esgotam
obrigatoriamente a árvore; buscas com objetivo podem encerrar antes.

A pasta de entrada e o destino dos resultados devem ser distintos. O programa
consulta os arquivos de entrada; JSONs e relatórios são gravados no destino de
saída. A árvore deve permanecer estática durante as medições.

### 2.1. Seletor nativo e navegação no terminal

`--selecionar-pasta` abre o diálogo de pastas do macOS via AppleScript; nas demais
plataformas usa `tkinter.filedialog.askdirectory`, quando Tcl/Tk está disponível.
O diálogo é síncrono. Quando o recurso gráfico está indisponível, a interface
informa a falha e usa o navegador do terminal. Cancelar o diálogo não troca a
pasta nem sobrescreve a preferência; com a flag direta, encerra a operação.

No navegador do terminal, arquivos e subpastas são numerados em ordem alfabética:

| Comando | Ação |
| --- | --- |
| Número de uma pasta | Entra na subpasta. |
| Número de um arquivo | Usa a pasta pai e sugere o nome como termo de busca. |
| `u` | Confirma a pasta atual. |
| `..` | Sobe para a pasta pai. |
| `p` | Permite digitar outro caminho. |
| `0` | Cancela a navegação. |

A navegação apenas lista nomes e tipos, sem ler conteúdos nem seguir symlinks.
O nome de arquivo escolhido é uma sugestão para busca por nome, mantendo o
critério de substring; outro arquivo cujo nome contenha esse trecho também
pode corresponder. Um alvo explícito em `--alvo` prevalece sobre a sugestão.
No modo conteúdo e no mapeamento, escolher um arquivo define apenas sua pasta;
o nome não se transforma em palavra a procurar no conteúdo. A etapa 2 usa a
sugestão quando não há alvo explícito; buscas individuais permitem confirmá-la
ou alterá-la no prompt.

### 2.2. Último caminho em JSON

A seleção confirmada é salva imediatamente, inclusive se a operação seguinte
for cancelada. O JSON padrão é `.file_hunter.json` na pasta do projeto, com
esquema `{"versao": 1, "ultimo_caminho": "/pasta/absoluta"}`. Esse caminho não
depende do diretório de onde o programa foi iniciado. `--config` permite usar
outro arquivo `.json` para a preferência.

Uma pasta explícita por `--raiz` também pode ser lembrada. No menu e nas flags
de seleção, a preferência válida é restaurada na ausência de `--raiz`. Uma
execução direta sem seletor mantém o padrão didático e não substitui a preferência
por ele. JSON ausente usa o padrão; JSON inválido ou pasta removida gera aviso
e usa o padrão. Falha ao salvar a preferência é informada sem impedir a busca.

A escrita usa um temporário exclusivo no mesmo diretório e substitui o JSON
depois de concluir a gravação. Cancelamento não apaga a seleção anterior.
`--sem-salvar` controla os resultados das buscas, não essa preferência.
Em experimentos, mantenha o arquivo de configuração fora da raiz pesquisada.

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
ou da seleção/restauração descrita na seção 2. As opções 8 e 9 permitem mudar
a pasta antes de escolher a tarefa.

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
entre suporte a fontes e OCR está na [arquitetura](ARQUITETURA.md#51-fonttools-no-ambiente-e-avaliação-para-pdfs).

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

## 8. Gráficos opcionais com Matplotlib

A opção **10 — Gráficos de resultados (opcional; requer Matplotlib)** solicita
um arquivo JSON ou uma pasta de resultados e o diretório dos PNGs. Após exportar,
retorna ao menu. Sem a biblioteca, informa o comando de instalação e permite
continuar usando as demais opções; nenhuma instalação é feita automaticamente.

Prepare a `.venv` conforme a seção 1. A instalação completa usa o mesmo arquivo:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

O único `requirements.txt` fixa pypdf 6.21.1 e Matplotlib 3.9.4, compatíveis com
Python 3.9. Sem essas bibliotecas, os recursos correspondentes informam a ausência;
o núcleo continua disponível.
Use o mesmo interpretador para instalar e executar. Para gerar dados e gráficos:

```sh
.venv/bin/python main.py --etapa 2 --alvo livro --alfa 100 --resultados resultados/entregas/etapa2
.venv/bin/python main.py --graficos resultados/entregas/etapa2 --saida-graficos resultados/graficos
.venv/bin/python -m funcoes.visualizacao resultados/entregas/etapa2 --saida resultados/graficos
```

Os dois últimos comandos são alternativas equivalentes. Aceitam vários arquivos
ou diretórios como entradas; a leitura de JSONs de diretórios não é recursiva.
Sem destino explícito, a saída é `resultados/graficos/`; na interface principal,
`--resultados` também redefine a base desse destino. `--graficos` usa resultados
existentes e rejeita opções de busca e `--sem-salvar`. `--saida-graficos` exige
`--graficos`. Para visualizar buscas feitas com `--sem-salvar`, execute e salve
um novo experimento, pois essa execução não terá produzido JSONs.

Cada grupo compatível gera um PNG com painéis para N, itens examinados, arquivos
lidos, g(n), pico tracemalloc em KiB e tempo em ms. As barras partem de zero e
mostram valores; g usa itens ou bytes. No mapeamento, g aparece como “Não se
aplica”; sem objetivo encontrado, como “Não encontrado”. Não se apresenta o zero
convencional do JSON como custo de um caminho encontrado. Alfa é identificado
quando há A*. As tabelas continuam sendo a fonte dos caminhos e rastros completos.

Experimentos, etapas, raízes, termos, modos, extensões, extratores e protocolos
distintos são separados. Duplicatas do mesmo algoritmo no mesmo grupo são
rejeitadas, inclusive em registros antigos sem identificação de experimento;
nesse caso, selecione um JSON por algoritmo. Arquivos PNG usam nomes exclusivos,
sem sobrescrever gráficos anteriores. A renderização usa Agg e dispensa janelas.

**Dependências transitivas.** Matplotlib instala bibliotecas como NumPy, Pillow
e fontTools. Na `.venv` verificada, fontTools 4.60.2 foi instalado junto ao
Matplotlib 3.9.4. Sua presença pode alterar a decodificação de fontes de alguns
PDFs pelo pypdf, mesmo sem solicitar gráficos. A avaliação histórica do acervo
real ocorreu sem fontTools; não atribuir a essa instalação ganhos de busca,
fidelidade ou OCR. A comparação controlada continua proposta na
[arquitetura](ARQUITETURA.md#51-fonttools-no-ambiente-e-avaliação-para-pdfs).
