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

## 8. Subpastas, formatos e nova revisão — entrega atual

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

## Estado final e limites

- Todas as sete entregas previstas estão implementadas. A suíte completa usa
  python3 -m tests; não usar -O, que removeria as asserções.
- Árvore deve permanecer estática durante as medições; verificações de symlinks
  não impedem trocas concorrentes entre verificar e abrir.
- Texto é classificado por extensão; pico corresponde a alocações Python.
- A* não garante ótimo nem economia, e alfa depende da escala de custo escolhida.
- Contagem e resultados são comparados entre as duas execuções, sem snapshot do
  sistema de arquivos. Números de tempo/memória dependem do ambiente e do cache.
- JSON com erro é rejeitado explicitamente. A gravação exclusiva evita colisões,
  mas não fornece transação persistente contra queda abrupta de processo/sistema.
