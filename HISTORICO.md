# Histórico de implementação

Registro para apoiar a documentação e a apresentação do projeto. Percentuais
seguem a média simples das sete entregas do README, não medem tempo ou cobertura.
Os hashes abaixo permitem consultar cada mudança com `git show HASH`.

## 1. Estrutura base — `31b2d4b`

- Criados módulos, pastas, README, AGENTS.md e .gitignore.
- Implementados `listar_dir`, dataclass `Metricas` e medições separadas.
- Gerador reproduzível com seed 2024: 40 pastas abaixo da raiz, profundidade 4,
  64 arquivos; 6 arquivos de texto com a palavra algoritmo.
- Verificados geração, listagem, reprodução byte a byte, symlinks e sintaxe.
- Buscas e interface ficaram como módulos com docstrings, respeitando o passo A.

## 2. BFS e DFS — `2be2731` — progresso estimado 36%

- Implementadas buscas por nome com deque.popleft/pop e realpaths visitados.
- Descoberta na expansão do pai, correspondência sem distinguir maiúsculas,
  listagem completa e custo acumulado do caminho.
- Criados menu, CLI e testes de ordem, custo, ciclos e ausência de resultado.
- Na árvore gerada, busca por livro: BFS abriu 30 pastas; DFS abriu 5; g=17.

## 3. UCS por nome — `7701989` — progresso estimado 54%

- Heap com prioridade, contador e nó; objetivos aguardam confirmação de custo.
- Custo da pasta só fica conhecido após expandi-la: entradas pendentes usam o
  custo do pai como limite inferior; candidaturas usam custo exato.
- Teste independente confirmou UCS com custo 4 contra primeiro resultado BFS 13.
- Verificados empates, ciclos, erros, menu e medições separadas.

## 4. Conteúdo e custo em bytes — `0a89a1b` — progresso estimado 68%

- BFS, DFS e UCS passaram a aceitar nome/conteúdo, compartilhando a leitura.
- Extensões de texto explícitas: .txt, .md, .py; UTF-8 com errors="ignore".
- g soma bytes dos textos das pastas do caminho; arquivos_lidos conta toda
  a exploração. Todos os textos da pasta são lidos, mesmo após uma correspondência.
- Teste: UCS escolheu 26 bytes contra 113 de BFS/DFS. Cobertos UTF-8 inválido,
  acentos, CRLF, arquivos vazios, binários excluídos e symlinks.

## 5. Revisão e otimização — `88dda64` — progresso mantido em 68%

- Corrigida normalização antecipada que ocultava symlinks antes de `..`.
- Leitura em blocos de 64 Ki caracteres, com cauda após casefold para reconhecer
  termos entre blocos. Contagem de bytes pelo deslocamento binário ao atingir EOF.
- Ordenação da listagem no próprio lugar e saída de BFS/DFS antes de processar
  filhos que não serão explorados.
- Criado `python3 -m tests` para executar a suíte completa.
- Em arquivo de 4 MiB, pico medido: integral 12.288,5 KiB; blocos 325,3 KiB.
  É uma medição local, não garantia de desempenho em outros ambientes.

## 6. Heurística e A* — `bf56771` — progresso estimado 86%

- Jaccard de bigramas, h=alfa*(1-similaridade), termo preparado uma vez por busca.
- Alfa finito, não negativo, padrão 1; disponível por --alfa na CLI.
- A* nos modos nome/conteúdo e opção 4 do menu. Compartilha motor com UCS;
  g fica separado de f, evitando incluir a heurística no custo do resultado.
- Mantida avaliação adiada: pastas pendentes usam g_pai+h; objetivos confirmados
  usam g_exato e h=0. Nenhuma pasta é listada sem contar como expansão.
- Teste com alfa=0 reproduziu UCS em resultados e métricas em ambos os modos.
- Contraexemplo com alfa=1000: A* abriu 2 pastas contra 3 de UCS, mas teve custo
  13 contra 3 no modo nome e 119 contra 9 no conteúdo. Confirma ausência de garantia
  de ótimo: a prioridade heurística pode antecipar um resultado mais caro.
- Na árvore gerada, A* por conteúdo com alfa=100 abriu 41 pastas, leu 52 textos
  e retornou g=320. Não houve economia de pastas nesse cenário.
- Verificados Jaccard, caracteres únicos/vazios, Unicode, pesos inválidos, ciclos,
  ausência de alvo, menu, CLI e regressões anteriores com `python3 -m tests`.

## 7. Persistência, relatórios e revisão final — `51c4f4c` — progresso 100%

- Menu/CLI salvam JSON automaticamente após as medições. Adicionados --sem-salvar
  e --resultados; executar continua isolado de gravação e interface.
- Esquema versionado com parâmetros, instante UTC, retornados e todas as métricas.
  Arquivos exclusivos com contador de colisões; sem sobrescrever execuções antigas.
- Conversor python3 -m funcoes.relatorio recebe arquivos/diretórios e produz
  tabelas Markdown de parâmetros e métricas, sem executar buscas. Valida esquema,
  números finitos e não negativos, arquivos vazios/corrompidos e valores escapados.
- Oito combinações de algoritmo/modo testadas em ida e volta JSON -> Markdown,
  incluindo colisões no mesmo instante, deduplicação, symlinks e entradas inválidas.
- Executados gerador, oito buscas reais e conversão em resultados/relatorio.md.
  Por nome/livro: pastas BFS=30, DFS=5, UCS=41, A*(alfa=100)=30, todos com g=17.
  Por conteúdo/algoritmo: pastas BFS=30, DFS=5, UCS=41, A*(alfa=100)=41, g=320.
- README consolida responsabilidades, dependências, custos das estruturas,
  instruções de comparação e limitações; todos os testes anteriores permanecem.
- Conferidos menu com --sem-salvar sem criar JSON, rejeição de saída com extensão
  inválida, sintaxe de todos os módulos e git diff --check.

## 8. Subpastas, formatos e nova revisão — `62b338d`

- Confirmado percurso recursivo nos quatro algoritmos: testes com quatro níveis
  abaixo da raiz localizaram PDF (inclusive .PDF), DOCX, XLSX, PPTX, ZIP, PNG,
  executável e arquivo sem extensão pelo nome, sem ler os binários.
- Mantida parada na pasta objetivo, de acordo com o contrato das buscas; não foi
  acrescentada uma coleta de todas as ocorrências da árvore sem definição de custo.
- Ampliado EXTENSOES_TEXTO para CSV/TSV, JSON/JSONL, LOG, marcação, configurações
  e fontes adicionais. O modo conteúdo mantém UTF-8, errors="ignore", leitura em
  blocos e soma de bytes reais, excluindo PDF/Office e outros binários.
- Help e menu distinguem busca de nome em qualquer formato de conteúdo textual.
  README inclui exemplos e limites de localização de PDF versus extração interna.
- Liberada a janela de comparação após achar o termo, reduzindo retenção de
  memória em arquivos com correspondência no início e termos longos.
- JSON passou a registrar extensoes_texto; relatórios exibem a política de texto
  para evitar comparar custos de seleções diferentes. Compatibilidade com registros
  antigos preservada: campo ausente é exibido como "não registrado".
- Suíte completa passou, incluindo regressões de formatos e metadados antigos.
- Validada a especificação esclarecida da etapa 3: `pedagogia` aparece apenas no
  conteúdo de documento.txt, dentro de _planos_pedagogicos_2024/. A* com alfa=1000
  leu 1 arquivo e abriu 2 pastas contra 2 arquivos e 3 pastas de UCS. g somou bytes
  do caminho; a redução de leituras foi observada nesse cenário, não garantida.
- Extração de texto de PDF/Office e OCR continuam sem implementação; exigem
  decisão explícita sobre extratores/dependências fora dos módulos autorizados.

## 9. Comparativo da etapa 3 e PDF autorizado — `232c85f`

- Adicionada tabela com as sete colunas pedidas: Algoritmo, Palavra no Conteúdo,
  Caminho, Pastas Abertas, Arquivos Lidos do Disco, Custo Total f(n), Tempo (ms).
- main.py --comparar executa UCS/A* por conteúdo com alvo padrão algoritmo;
  --comparativo no conversor gera a tabela de JSONs existentes, sem novas buscas.
- f final é g no objetivo confirmado (h=0). Sem resultado, f não é definido e
  aparece como —. JSON agora registra avaliacao_final com g/h/f, opcional para
  leitura de registros antigos. Dados de raízes/políticas diferentes não se misturam.
- Usuário autorizou extrator externo para PDF, alterando a regra inicial de usar
  somente biblioteca padrão. Esclarecido que pypdf é externo; instalado pypdf
  6.21.1 na .venv, com versão direta fixada em requirements.txt.
- Novo adaptador funcoes/pdf.py extrai todas as páginas e conta bytes de read,
  readline e readinto, inclusive releituras após seek. Textos simples preservam
  a leitura em blocos. Buscas por nome permanecem independentes da instalação.
- Importação opcional ocorre antes das medições. extrator_pdf identifica versão
  no JSON/relatório; parser não interfere nas políticas de fila, pilha e heap.
- Testes de PDF real multipágina, comprimido, sem texto, protegido/corrompido,
  ausência de dependência e integração nos quatro algoritmos. Testes da tabela
  verificam sete colunas, filtros, custos 9/109 bytes, caminhos, ausência e legado.
- Exemplo executado em docencia/exemplo_pdf: algoritmo aparece apenas dentro de
  documento.pdf. Com alfa=100000, UCS abriu 3 pastas/leu 2 arquivos; A* abriu
  2/leu 1; ambos tiveram f final=5582 bytes. Resultado em resultados/comparacao_pdf/tabela.md.
  Esse peso foi escolhido para o exemplo, não é recomendação universal.
- OCR e leitura de conteúdo Office permanecem fora do escopo autorizado.

## 10. Padronização obrigatória das métricas — `ff40143`

- Centralizados rótulos e unidades em metricas.py para Nós expandidos (N), itens
  examinados, arquivos processados/lidos, g, pico de memória e tempo de execução.
- Adicionado alias nos_expandidos de pastas_abertas, sem manter dois contadores.
  Campos originais da dataclass e dos JSONs preservados.
- CLI e relatório geral agora mostram o padrão completo. Comparativo mantém as
  sete colunas solicitadas e acrescenta a tabela de métricas principais, incluindo
  g e consumo de memória que não estavam na tabela original.
- Mantidos time.perf_counter em ms e pico tracemalloc em KiB, em execuções
  independentes. RSS não é medido nem apresentado como se fosse pico tracemalloc.
- Campo medicao nos JSONs documenta funções, unidades e separação; metadados
  incompatíveis são rejeitados. Registros antigos sem medicao continuam aceitos.
- Testes verificam perf_counter com intervalo controlado de 125 ms, alocação
  rastreada, N por scandir, itens versus leituras, g em itens/bytes e compatibilidade
  de registros; testes anteriores de buscas, PDF e tabela permanecem ativos.
- Executadas as suítes com e sem o extra PDF, verificação de sintaxe e comparação
  real; JSONs com metadados de instrumentação e relatórios completos gerados em
  resultados/metricas_padrao/. A tabela PDF anterior também foi atualizada.

## 11. Fechamento das lacunas das entregas acadêmicas — entrega atual

- Após auditoria, corrigida a abrangência dos percentuais anteriores: os 100%
  registrados até a seção 10 não cobriam o detalhamento completo das três etapas.
- Confirmado pelo usuário: global é SOMENTE BFS/DFS da etapa 1. Implementado
  mapear sem alvo e sem ler conteúdos, retornando todos os arquivos em ordem.
- Etapa 1 passou a entregar resumo, primeiros 10 BFS/DFS lado a lado, lista completa
  de caminhos relativos e cronologia das expansões. Árvore padrão: N=41 e 64
  arquivos em ambos, ordem diferente a partir da quinta descoberta.
- Busca por nome passou a retornar um único arquivo na pasta objetivo selecionada.
  A expansão inteira continua contada e encontrados pode incluir outros candidatos.
- Etapa 2 compara os quatro algoritmos para livro: tabela pedida, percurso e soma
  dos custos locais no caminho até o alvo. Na árvore padrão, N=30/5/41/30 com
  alfa=100 e g=17 itens para BFS/DFS/UCS/A*, respectivamente.
- Etapa 3 preserva UCS/A* por conteúdo e acrescenta fórmula no próprio relatório,
  diferença numérica de N e arquivos lidos e diretórios não expandidos por A*.
  Na árvore padrão com alfa=100, ambos N=41, leituras=52 e g=320 bytes: sem redução
  neste cenário. A demonstração positiva com PDF permanece disponível.
- --etapa 1/2/3 e opções 5/6/7 do menu executam entregas específicas. --comparar
  permanece como atalho da etapa 3. Cada lote salva JSONs e etapa_N.md; conversor
  pode reconstruir cada relatório a partir dos JSONs sem refazer as buscas.
- Acrescentados escopo/etapa, identificação comum de experimento, base dos caminhos
  e rastro [{diretorio,custo_local,g}]. Validação confere N, pais, custos e objetivo.
  Tempo e memória coletam rastros separados e verificam igualdade antes de publicar.
- Metadados novos são opcionais para registros antigos; cronologias globais não
  são inventadas para JSONs de buscas interrompidas no alvo.
- Tabelas acadêmicas KB usam 1000 bytes; pico padrão KiB usa 1024. Conversão testada.
- Testes específicos: ordem BFS/DFS conhecida, todos os arquivos, primeiros 10,
  ausência, raiz vazia, ciclos, PDF por nome sem extrator, primeiro alvo, quatro
  algoritmos, g=6/6/4/6 no cenário controlado, conteúdo=17/26 bytes e validação de
  rastro. Testes anteriores permanecem para preservar métricas/PDF/heurística.
- UCS mantém a avaliação adiada: não há como conhecer len(itens) sem abrir a pasta.
  Menor g acumulado não garante menor custo local isolado; o relatório explicita
  esse compromisso sem pré-listagens gratuitas. A* continua sem garantia de ótimo.
- Executadas as suítes com/sem PDF, o menu da etapa 1 sem gravação, rejeição de
  argumentos incompatíveis, sintaxe e reconstrução dos três relatórios dos JSONs.
  Entregas reais em resultados/entregas/etapa1, etapa2 e etapa3. Demonstração PDF
  com redução de uma pasta e uma leitura em resultados/entregas/demonstracao_pdf.

## Estado final e limites

- As entregas detalhadas das três etapas estão implementadas. Mapeamento global
  é exclusivo de BFS/DFS; demais buscas continuam orientadas ao alvo e podem
  explorar toda a árvore se necessário, inclusive quando não existe resultado.
  A suíte completa usa
  python3 -m tests; não usar -O, que removeria as asserções.
- Árvore deve permanecer estática durante as medições; verificações de symlinks
  não impedem trocas concorrentes entre verificar e abrir.
- Texto é classificado por extensão; pico corresponde a alocações Python.
- A* não garante ótimo nem economia, e alfa depende da escala de custo escolhida.
- Contagem e resultados são comparados entre as duas execuções, sem snapshot do
  sistema de arquivos. Números de tempo/memória dependem do ambiente e do cache.
- JSON com erro é rejeitado explicitamente. A gravação exclusiva evita colisões,
  mas não fornece transação persistente contra queda abrupta de processo/sistema.
- PDF exige o extra opcional pypdf. Comprimir PDF não impede extração; documentos
  apenas imagem podem não ter texto. Protegidos/corrompidos interrompem com erro.
