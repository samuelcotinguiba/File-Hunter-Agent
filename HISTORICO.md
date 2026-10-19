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

## 11. Fechamento das lacunas das entregas acadêmicas — 46dcce8

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

## 12. Auditoria do timer e coordenação das medições — f1ef17a

- Revisada a contagem de tempo: a fórmula perf_counter com conversão para ms
  estava correta e já excluía o perfil tracemalloc. Não houve correção de unidade
  ou subtração de tempo; o ajuste foi na ordem das execuções comparativas.
- Antes, cada algoritmo executava tempo e perfil antes do próximo algoritmo.
  Agora _medir_lote, compartilhado pela busca individual e etapas, cronometra
  todos os algoritmos antes de iniciar qualquer perfil. A criação dos registros
  só ocorre após terminar e validar as medições do lote inteiro.
- O timer inclui a chamada inteira da busca, com E/S, heurística, contadores e
  rastro; exclui menu, impressão, registros, JSON, Markdown e perfil de memória.
  Mede tempo decorrido, não CPU isolada nem tempo exclusivo de disco.
- Resultados, contadores e rastros continuam comparados entre tempo e memória;
  erros ou divergências impedem publicar o lote. Nenhum contador soma as buscas.
- JSON ganha protocolo_lote opcional para identificar a ordem nova. Registros
  antigos continuam válidos, sem presumir essa ordem. Relatórios separam os
  protocolos e descrevem escopo do timer, cache e uma amostra por algoritmo.
- Teste com relógio controlado mantém 125 ms mesmo quando o perfil simula 1000 s
  e a criação do registro simula 500 s. Verifica fases nas etapas 2/3, busca
  individual, estado novo, contadores, compatibilidade e falhas antes de publicar.
- README e AGENTS atualizados com as escolhas e justificativas. A ordem dos
  algoritmos permanece fixa; não há limpeza de cache, garantia de tempo menor
  ou tratamento estatístico. A mudança evita perfis intercalados, sem eliminar
  a influência de dados aquecidos e carga do sistema.
- A execução real revelou também que a tabela da etapa 3 ainda mostrava caminhos
  absolutos, diferindo das demais entregas. Corrigida para usar base_caminhos,
  mantendo caminhos relativos estáveis na conversão; testes cobrem bases distintas.
- Verificações concluídas: python3 -m tests (base, sem extrator instalado),
  .venv/bin/python -m tests (incluindo PDF), compileall e git diff --check.
  Árvore regenerada: 40 pastas abaixo da raiz, 64 arquivos, seed 2024.
  Etapas reais e JSONs/Markdown em resultados/revisao_timer/etapa1, etapa2,
  etapa3 e pdf; relatórios de conteúdo reconstruídos dos JSONs pelo conversor.
  Mapeamento: ambos N=41/64 arquivos; nome com alfa=100: N=30/5/41/30 e g=17;
  conteúdo padrão: UCS/A* N=41, 52 leituras, g=320 bytes. No exemplo PDF com
  alfa=100000: N=3/2, leituras=2/1, g=5582 bytes, respectivamente.
  Os contadores reais preservam as entregas; tempos são amostras deste ambiente.

## 13. Revisão de correção, fronteira e PDF — 5e05856

- A suíte inicial passou. Novos testes reproduziram dois erros antes das correções:
  PDF com texto extraído 'fim' respondia positivamente por 'fim\n', devido a uma
  quebra final artificial; o mapeamento aceitava BFS/DFS duplicados no mesmo
  experimento e sobrescrevia uma cronologia nas colunas dos primeiros 10.
- PDF agora insere separadores somente entre páginas, equivalendo a unir os
  textos extraídos com '\n'. Mantém casefold, leitura integral, contagem de bytes,
  páginas vazias e correspondências que atravessam páginas. Janela temporária
  é liberada após cada comparação, sem prometer memória limitada para pypdf.
- Relatório da etapa 1 rejeita duplicatas no mesmo grupo e pede selecionar um
  JSON por algoritmo/experimento. Experimentos diferentes permanecem separados;
  nenhuma cronologia é descartada silenciosamente na comparação global.
- Otimizado o motor compartilhado por UCS/A*: pasta com alvo insere somente sua
  candidatura. Custos e h >= 0 impedem que descendentes saiam do heap antes desse
  objetivo, inclusive nos empates. A parada continua na retirada da candidatura,
  preservando a concorrência de outros ramos e a garantia de UCS em árvore estática.
  Sem objetivo local, filhos entram diretamente no heap, sem lista intermediária.
- Testes cobrem alvo na raiz com 64 filhos, nenhuma consulta realpath aos filhos,
  itens e bytes completos da pasta objetivo, outros candidatos mais baratos,
  ordem das expansões, alfa zero e busca exaustiva na ausência de objetivo.
  PDF usa referência independente com uma, duas e três páginas, termos entre
  páginas e com quebra final; confirma custo igual ao encontrar cedo ou não achar.
  As regressões falharam antes da correção e passaram depois.
- Amostra local com alvo na raiz e 128 filhos vazios: quatro combinações
  UCS/A* × nome/conteúdo mantiveram caminhos e métricas de contagem idênticos;
  realpath caiu de 129 para 1. Por nome: N=1, itens=129, g=129; por conteúdo:
  N=1, itens=129, leituras=1, g=9 bytes. Pico de alocações Python em KiB:

  | Algoritmo/modo | Antes | Depois |
  | --- | ---: | ---: |
  | UCS/nome | 80,441 | 38,016 |
  | A*/nome | 69,330 | 38,282 |
  | UCS/conteúdo | 106,271 | 106,326 |
  | A*/conteúdo | 106,654 | 106,678 |

  O conteúdo continua dominado pelo buffer de leitura; não houve redução de pico
  nesse caso. Números locais, sujeitos a estado do interpretador e alocações,
  sem promessa de ganho universal ou classificação dos algoritmos. Arquivos em
  resultados/revisao_codigo/otimizacao_antes.json e otimizacao_depois.json;
  árvore local em docencia/exemplo_otimizacao, ambos ignorados pelo Git.
- Documentadas as justificativas em README e AGENTS, sem novas dependências.
  Progresso das três entregas permanece 100% do escopo implementado; esta revisão
  cobre regressões adicionais e não significa ausência de outros defeitos.
- Verificações finais passaram: python3 -m tests (sem extra PDF),
  .venv/bin/python -m tests (com PDF), compilação de sintaxe com cache em /private/tmp
  e git diff --check. Executadas as três etapas e o exemplo PDF pelo CLI, com
  JSONs validados e relatórios reconstruídos idênticos aos gravados. Artefatos em
  resultados/revisao_codigo/etapa1, etapa2, etapa3 e pdf. Contagens padrão mantidas:
  global N=41/64 arquivos; nome N=30/5/41/30 e g=17; conteúdo UCS/A* N=41,
  leituras=52, g=320 bytes; PDF N=3/2, leituras=2/1, g=5582 bytes.

## 14. Consolidação da documentação acadêmica — ef0489a

- README reorganizado como apresentação técnica: resumo, palavras-chave,
  objetivos, delimitação, etapas, estruturas, métricas, reprodução e limites.
  Preservados comandos de execução, escopo por etapa e indicação de pypdf como
  dependência externa opcional. Nenhuma norma editorial é presumida.
- Criado docs/ARQUITETURA.md com modelo de diretórios/custos, diagrama de
  dependências reais, sequência das medições, responsabilidades dos módulos,
  representações da fronteira, invariantes e análise de custo computacional.
- Explicitada a avaliação adiada: prioridade de pasta pendente usa g do pai;
  listagem/leitura revela o custo local. Acrescentada justificativa de correção
  de UCS em árvore finita e estática com custos não negativos e o argumento
  para dispensar descendentes de uma pasta que já contém objetivo confirmado.
- A* documentado como adaptação heurística sem garantia de ótimo; separados
  prioridade pendente, g exato e f da candidatura objetivo. Preservadas unidade
  de alfa, equivalência com UCS quando alfa=0 e ausência de poda por similaridade.
- Criado docs/METODOLOGIA.md com questões de investigação, variáveis, conjuntos
  de dados, definições operacionais, duas fases de medição, colunas solicitadas,
  resultados de referência e matriz que relaciona requisitos à suíte existente.
- Incluídas ameaças à validade: uma amostra por algoritmo, ordem fixa, cache,
  ausência de snapshot, limites do tracemalloc, classificação por extensão,
  extração PDF e persistência sem transação atômica do lote. Repetições e análise
  estatística são descritas somente como possíveis extensões.
- Fontes oficiais de collections/deque, heapq, os/scandir, perf_counter,
  tracemalloc e extração pypdf consultadas para fundamentar as APIs, com links
  junto às afirmações e referências técnicas nos documentos.
- AGENTS atualizado com o mapa documental e regras para preservar rigor e
  rastreabilidade. Não houve alteração de algoritmos, métricas ou dependências.
  Progresso funcional permanece 100% do escopo implementado; a atualização é
  documental e não representa aprovação docente ou ausência de defeitos.
- Validação: 48 links locais conferidos, blocos Markdown balanceados e 18
  dependências do diagrama confrontadas com os imports reais via análise estática.
  Resultados de referência das três etapas reproduzidos com alfa=100, incluindo
  41 pastas/64 arquivos no mapeamento e 52 leituras na busca de conteúdo.
  Opções dos exemplos conferidas com o help dos dois CLIs. Suítes com e sem
  extra PDF e git diff --check passaram; não foram acrescentados testes que
  apenas reproduzam a organização dos documentos.

## 15. Validação com Docencia/Fontes e PDFs reais — `c345ff5`

- Acervo localizado em ../Docencia/Fontes, separado da árvore didática interna:
  11 diretórios incluindo a raiz, 62 PDFs e 428.430.326 bytes armazenados, sem
  symlinks. Fonte da implementação: ef0489a0c9d8e1de89063bcad51925ec773754d5;
  ambiente Python 3.9.6, Darwin/arm64, pypdf 6.21.1.
- Inventário inicial preservou nomes, tamanhos e mtime_ns. Etapa 1 comparada com
  enumeração independente: BFS/DFS N=11, itens=72, arquivos=62 e leituras=0.
  Primeiros 10 iguais; primeira diferença de cronologia na posição 23.
- Etapa 2, alvo livro e alfa=100: BFS/DFS/A* retornaram Livro Desenvolvimento
  Mobile.pdf em Fontes DMN, N=3 e g=17. UCS retornou LIVRO_UNICO_GTI.pdf,
  N=10 e g=13, confirmado pelo oráculo independente dos quatro nomes-alvo.
- Auditoria de extração separada dos algoritmos processou 62 PDFs sem exceção,
  7.592 páginas, 6.940 com texto não vazio e 20 PDFs com algoritmo no texto
  extraído. Sete PDFs não forneceram texto. Registrados 3.714 avisos sobre ausência
  de fontTools para suporte completo a determinadas codificações CFF Type1.
  A conclusão é sobre a extração disponível, sem presumir ausência visual do
  termo, presença de camada OCR ou fidelidade integral das fontes.
- Etapa 3 integral, alvo algoritmo e alfa=100: UCS/A* N=10, itens=60, 19
  correspondências descobertas, 50 PDFs lidos e g=f=6.204.185 bytes. Ambos
  selecionaram Fontes PCD/LIVRO SISTEMAS-DIGITAIS.pdf. A subpasta de ferramentas
  de GD, com 12 PDFs, não foi expandida pelas buscas; a auditoria não orientou
  previamente a fronteira nem substituiu as leituras das medições.
- Tempos das buscas: UCS=201.669,849 ms e A*=198.947,927 ms. Picos tracemalloc:
  299.214,132 KiB e 299.215,223 KiB, aproximadamente 292,20 MiB cada. Perfis
  de memória duraram cerca de dez minutos por algoritmo e ficaram fora dos tempos.
  Caminhos, contadores e rastros coincidiram em cada par tempo/memória.
- Custos de conteúdo por diretório foram agregados independentemente da ordem
  de busca e comparados com todas as expansões. Confirmado mínimo global de
  6.204.185 bytes. Total de bytes dos ramos explorados: 260.270.782, distinto
  do g final. Não houve economia de N/leituras por A*; diferença temporal local
  não demonstra superioridade estatística.
- Conferência final preservou conjunto de arquivos, tamanhos e mtimes. Os três
  relatórios foram reconstruídos dos JSONs e coincidiram com os originais.
  Trata-se de verificação de metadados, sem snapshot ou garantia criptográfica.
- Criado docs/VALIDACAO_DOCENCIA.md e atualizados README, metodologia e AGENTS.
  Logs locais do extrator passaram a ser ignorados pelo Git. Artefatos em
  resultados/validacao_docencia/1792399791315981000/, incluindo inventário,
  ambiente, auditoria, oráculos, verificações e as subpastas etapa1/2/3.
- Nenhuma dependência ou algoritmo foi alterado. A suíte com PDF passou antes
  da avaliação. A validação operacional das três etapas está concluída, com as
  ressalvas de extração identificadas; não se declara pesquisa visual integral
  dos sete documentos sem texto. O escopo funcional implementado permanece 100%.

## 16. Fórmula da heurística e demonstração de poda

- Os dois requisitos já estavam presentes na arquitetura e na metodologia.
  A apresentação foi reforçada no README: fórmula de Jaccard de bigramas,
  h(n)=alfa×(1−J), f=g+h e distinção entre prioridades pendentes e objetivos.
- Incluído cálculo numérico para pedagogia, com alfa=1000: planos pedagógicos
  têm J=7/21 e h≈666,667; imagens auxiliares têm J=2/24 e h≈916,667.
  O cálculo usa casefold, inclui os caracteres do nome e dispensa modelos de ML.
- Tabelas passaram a explicitar ΔN e ΔL. No cenário controlado, UCS/A* abriram
  3/2 pastas e leram 2/1 arquivos: economia de uma pasta (33,33%) e um arquivo
  (50%), com mesmo arquivo objetivo e g. Árvore padrão e acervo real mantêm
  diferenças zero, sem atribuir redução a A* quando ela não foi observada.
- Documentada a interpretação de poda como trabalho evitado na execução, sem
  descarte permanente por nome ou garantia de ótimo. Leituras contam arquivos
  abertos/lidos pela aplicação, por execução, sem equivalência a acessos físicos.
- Conferidos valores de Jaccard com a implementação e contadores do acervo com
  os JSONs preservados. A conferência documental não repete a leitura dos 62 PDFs.
- Verificações desta entrega: suíte completa com PDF, cenário controlado,
  conferência dos exemplos numéricos, links locais e git diff --check.
- Alteração documental; algoritmos e dependências permanecem iguais. Escopo
  funcional implementado permanece 100%, sujeito às limitações já registradas.

## 17. Consolidação do código e justificativas de arquitetura — `a124df9`

- Revisão dos módulos, APIs, testes e imports. Não foram encontrados imports
  sem uso aparente. Preservadas as entradas públicas bfs/dfs, usadas como API,
  os testes de regressão, os relatórios e os mecanismos exigidos de medição.
- buscar/mapear passaram a compartilhar _percorrer: uma única implementação de
  expansão, custos, visitados, rastro e fronteira BFS/DFS. Removida a duplicação
  do laço de mapeamento e a lista temporária de subpastas. Inserção direta na
  deque preserva a ordem dos arquivos e inverte somente os filhos no DFS.
  popleft/pop é selecionado uma vez por chamada.
- Corrigido erro reproduzido de validação na API: tipos não textuais geravam
  AttributeError no casefold; A* também preparava bigramas antes de rejeitar None.
  validar_busca agora exige str não vazio, valida o modo e retorna o termo
  normalizado. UCS/A* validam nas entradas públicas; o motor de heap recebe esse
  termo pronto, sem repetir validação. Alfa zero permanece equivalente a UCS.
- Acrescentada regressão em test_revisao.py: quatro estratégias, nome/conteúdo,
  alvos vazios ou inválidos e A* com alfa zero/positivo, usando raiz inexistente
  para conferir a rejeição antes de expandir diretórios.
- Comparação anterior/posterior preservou oito resultados completos: caminhos,
  contadores e rastros. Cenário largo com 1.024 subpastas: pico de 509,127 para
  500,631 KiB em BFS e DFS, economia local de 8,496 KiB (aproximadamente 1,67%).
  Uma amostra por versão/estratégia, sem benchmark comparativo de tempo.
  Artefatos em resultados/revisao_final/antes.json e depois.json.
  Removido somente o cenário temporário criado para a aferição, após conferir
  seu conjunto de arquivos/diretórios com o rastro; registros e logs preservados.
- Atualizados AGENTS, README, arquitetura e metodologia: motores compartilhados,
  validação de entrada, grafo de dependências, matriz de decisões com justificativas
  e compromissos e descrição de como o projeto foi construído por etapas.
- Verificações: suítes com/sem extra PDF, entregas CLI na árvore didática,
  reconstrução idêntica dos três relatórios, revisão de imports, 67 links/âncoras
  locais e git diff --check. Nenhum erro nas verificações finais.
  A avaliação integral e demorada dos 62 PDFs não é repetida; seus resultados
  permanecem vinculados à revisão originalmente medida.
- Nenhuma dependência foi acrescentada. Escopo funcional implementado permanece
  100%, com as limitações de extração PDF/OCR e de medição já documentadas.

## 18. Proposta futura de suporte a fontes com fontTools — entrega atual

- Documentado o possível uso opcional de fontTools para auxiliar o pypdf em
  determinados mapeamentos de fontes CFF Type1 incorporadas sem ToUnicode.
  Motivação: avisos do acervo e possível redução de caracteres incorretos e
  falsos negativos, sem presumir ganho antes de conferir documentos de referência.
- Explicada a diferença entre biblioteca auxiliar, fontes do sistema e OCR.
  A proposta não resolve texto armazenado somente como imagens ou contornos.
- Registrados o isolamento no adaptador PDF e um protocolo futuro com referências
  textuais, ambientes equivalentes, versões identificadas e novas medições
  independentes de tempo/memória. Remover avisos não é critério suficiente.
- Conferidos o código local e a fonte oficial de pypdf 6.21.1. Na consulta de
  19/10/2026, a documentação publicada de fontTools exige Python 3.11+, enquanto
  o projeto utiliza 3.9.6; eventual adoção deverá avaliar versão compatível ou
  migração testada do interpretador.
- Atualizados README, arquitetura, validação do acervo e AGENTS com o estado
  proposto. Nenhuma instalação, alteração de código, dependência ou resultado
  histórico. A versão/disponibilidade de fontTools ainda não é metadado JSON.
- Verificação documental: links locais e âncoras, blocos Markdown e git diff
  --check; ambiente atual confirmado como pypdf 6.21.1 sem fontTools.
- Escopo funcional implementado permanece 100%; a melhoria descrita é trabalho
  futuro e não integra esse percentual nem representa garantia de extração.

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
