# File Hunter Agent

## Escopo e dependências

- Implementar por etapas. Passo A concluído; continuação autorizada pelo usuário.
  Entrega atual: buscas, medições, menu/CLI, JSON e relatórios Markdown concluídos.
- Atualizar docs/HISTORICO.md a cada entrega com mudanças, decisões, verificações,
  limitações e progresso estimado, para apoiar a documentação final do usuário.
- Usar apenas biblioteca padrão do Python 3: collections, heapq, os, time,
  tracemalloc, json e argparse; dataclasses é necessário para a dataclass exigida.
- Seleção nativa autorizada posteriormente: subprocess apenas na interface do
  macOS e tkinter opcional nas demais plataformas, ambos da biblioteca padrão.
  Testes de interface podem usar unittest.mock e módulos de apoio da biblioteca
  padrão, sem abrir janelas. Não acrescentar pacotes externos para essa função.
- Exceção posterior autorizada pelo usuário: pypdf opcional para conteúdo PDF,
  fixado em requirements.txt e instalado somente na .venv (com suas dependências
  transitivas). pypdf NÃO é biblioteca padrão. Não ampliar outras dependências.
- Não reutilizar classes de BST. O nó é um diretório.
- Matplotlib somente em eventual módulo opcional de visualização, nunca nas buscas
  ou métricas; não instalar dependências para o passo A.

## Documentação acadêmica e rastreabilidade

- O [README.md da raiz](../README.md) é a apresentação única do projeto e aponta
  diretamente para a [pasta docs/](./), com links para cada documento.
  Manter instruções detalhadas em [USO.md](USO.md), objetivos e processo de
  construção em [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md) e histórico em
  [HISTORICO.md](HISTORICO.md). Os contratos de manutenção ficam apenas em
  docs/AGENTS.md, sem cópia na raiz ou README adicional em docs/.
  Os caminhos citados como docs/... neste contrato são relativos à raiz do projeto.
  [ARQUITETURA.md](ARQUITETURA.md) detalha o modelo computacional,
  dependências, estruturas, avaliação adiada, invariantes e complexidade.
  [METODOLOGIA.md](METODOLOGIA.md) define protocolo experimental,
  métricas, resultados de referência, rastreabilidade dos testes e limitações.
- Manter linguagem técnica formal e descrições compatíveis com o código.
  Distinguir garantias condicionais, resultados observados e trabalhos futuros.
  Não apresentar avaliação adiada como conhecimento antecipado do custo local,
  similaridade como heurística admissível, leituras como operações físicas ou
  pico tracemalloc como RSS.
- Diagramas Mermaid descrevem módulos e chamadas sequenciais das buscas em um
  processo Python. A interface macOS pode aguardar o auxiliar osascript para
  seleção; não atribuir concorrência às buscas nem componentes ausentes.
- A execução é síncrona: não há asyncio, threads ou processos nas buscas.
  Python não torna scandir/open/extração PDF assíncronos automaticamente.
  Preservar ordem de expansão, parada e isolamento das medições; eventual
  concorrência é uma extensão que exige protocolo e verificação próprios.
- Preservar exemplos reproduzíveis, vínculos entre requisitos e testes e a
  identificação da revisão/ambiente na análise acadêmica. Campos não registrados
  automaticamente, como hardware e revisão Git do experimento, devem ser
  identificados como informação externa, sem inventá-los nos JSONs.
- Usar fontes técnicas primárias para fundamentar APIs e justificar decisões
  específicas pela implementação. Não declarar conformidade ABNT ou outra norma
  editorial sem requisito e verificação próprios.
- Em acervos reais, distinguir auditoria dos formatos e execução dos algoritmos:
  a auditoria não fornece custos previamente conhecidos à fronteira nem substitui
  leituras medidas. Manter os dados originais e resultados em raízes distintas.
  Registrar arquivos sem texto extraível e avisos do parser, sem interpretar
  ausência de texto como ausência visual do termo. Logs são artefatos locais.

## Decisões de design

1. Nó = diretório. Expandir = listar seu conteúdo com os.scandir; conta como uma
   pasta aberta.
2. Arquivo é descoberto quando o pai é expandido e ele aparece na listagem.
   A definição será idêntica em BFS e DFS.
3. Etapa 2: g(n) é a soma de len(itens), arquivos e subpastas, de cada diretório
   do caminho da raiz até o nó, incluindo ambos. Objetivo: nome do arquivo contém
   o termo, sem diferenciar maiúsculas e minúsculas.
4. Etapa 3: g(n) é a soma dos bytes lidos dos arquivos de cada pasta do caminho.
   Objetivo: conteúdo contém o termo. Ler somente texto, com errors="ignore".
5. Guardar realpath dos diretórios visitados para controle de ciclos; nunca
   seguir symlinks. A busca futura manterá os visitados; listar_dir apenas lista.
6. Heap sempre contém tuplas (prioridade, contador, nó) para desempate.
7. BFS usa deque.popleft(); DFS usa deque/list.pop().
8. Medir tempo com time.perf_counter e memória com tracemalloc em execuções
   separadas, pois tracemalloc distorce o tempo. Recriar estado de busca para cada
   execução; não reutilizar visitados ou métricas entre medições. Nos lotes das
   etapas, executar todos os tempos primeiro e todos os perfis de memória depois.
9. Heurística: h(n) = alfa * (1 - similaridade(nome_pasta, termo)), com
   Jaccard de bigramas. Não é admissível; A* não
   garante caminho ótimo.

## Contratos do passo A

- listar_dir retorna uma lista de os.DirEntry ordenada por nome. Exclui links
  simbólicos e entradas que não são arquivos regulares nem diretórios. Não abre
  uma raiz que seja symlink e rejeita componentes simbólicos no caminho.
- Erros de acesso e caminhos ausentes são propagados ao chamador.
- Métricas de contagem são atualizadas pelas buscas futuras, não pela listagem.
- custo_g é o custo acumulado do caminho, não o custo de toda a exploração.
- Tempo é expresso em ms; pico de memória em KiB (campo pico_mem_kb).
- Padrões obrigatórios de apresentação em CLI e relatórios: Nós expandidos (N),
  Arquivos/Itens examinados, Arquivos processados/lidos, Custo do Caminho g(n), Consumo de
  Memória e Tempo de Execução. Centralizar rótulos e unidades em metricas.py.
- N é pastas_abertas; propriedade nos_expandidos é alias de leitura, sem contador
  duplicado. itens_examinados conta arquivos/subpastas listados; arquivos_lidos
  conta conteúdos realmente abertos/lidos, não só nomes inspecionados.
- Memória obrigatória usa tracemalloc.get_traced_memory()[1]/1024, em KiB de
  alocações Python. Não chamar esse valor de RSS ou memória total do processo.
  Tempo obrigatório é a diferença de time.perf_counter()*1000, em outra execução.
- O gerador usa seed fixa 2024 e um gerador congruencial próprio. Reexecutá-lo
  sobrescreve apenas seus arquivos conhecidos, sem apagar outros arquivos.

## Contratos de BFS e DFS

- Etapa 1: modo de mapeamento global EXCLUSIVO de BFS/DFS, sem alvo e sem leitura
  de conteúdos. Percorrer todas as pastas, retornar todos os arquivos na ordem de
  descoberta e registrar as expansões para comparar os percursos.
- Etapa 2: busca por nome encerra na pasta objetivo, retornando somente o primeiro
  arquivo correspondente (ordem da listagem). A listagem inteira é examinada;
  arquivos_encontrados conta todas as correspondências descobertas nessa expansão.
- Etapa 3: conteúdo mantém retorno dos correspondentes da pasta objetivo.
- Acumular g incluindo a listagem da raiz e da pasta do resultado. Sem resultado,
  custo_g permanece zero. arquivos_lidos permanece zero na busca por nome.
- Ordem alfabética de expansão para irmãos, inclusive DFS (empilhamento inverso).
- Marcar realpath ao inserir na fronteira; usar uma única fronteira deque e
  compartilhar a lógica de expansão entre BFS e DFS para manter a descoberta igual.
- buscar e mapear reutilizam o motor privado _percorrer. Somente mapear entrega
  termo=None ao motor; buscar rejeita alvos vazios ou que não sejam str.
  Coletar arquivos do mapeamento na ordem da listagem e inserir subpastas
  diretamente na deque, invertendo apenas a inserção do DFS, sem lista auxiliar.
  Escolher popleft/pop uma vez ao inicializar o percurso.
- Erros de acesso são propagados, sem apresentar busca incompleta como sucesso.
- A execução de memória repete a busca com estado novo. Seu resultado deve ser
  igual ao da execução de tempo; divergências são reportadas. Isso não detecta
  todas as alterações de conteúdo ou metadados entre chamadas.

## Contratos de UCS por nome

- Não listar uma pasta para descobrir sua prioridade antes de contabilizar a
  expansão. Como len(itens) só é conhecido após abrir a pasta, usar o custo do
  pai como limite inferior na entrada de expansão do heap.
- Ao expandir, calcular o custo exato incluindo a própria pasta. Se houver
  correspondências, inserir candidatura a objetivo no heap com esse custo.
  Encerrar apenas quando a candidatura for removida do heap; custos não negativos
  garantem que nenhum candidato de custo menor ficou pendente numa árvore estática.
- Heap contém sempre (prioridade, contador, nó). Nó é (pasta, None, g_pai) para
  expansão ou (pasta, correspondências, g_exato) para candidatura já expandida.
  Remover candidatura não conta como nova expansão e não relista a pasta.
- Se a pasta expandida contém um objetivo, inserir somente sua candidatura e
  dispensar o preparo dos descendentes. Custos locais e h são não negativos:
  um filho teria prioridade >= g dessa candidatura, que também venceria empates
  por ter sido inserida antes. Continuar pelo heap para permitir que outra pasta
  produza objetivo mais barato; não retornar imediatamente ao descobrir o alvo.
  A listagem e leitura da pasta objetivo permanecem completas e contabilizadas.
- Sem objetivo local, inserir os filhos diretamente no heap, sem lista auxiliar
  de subpastas. Preservar ordem da listagem, visitados e desempates.
- arquivos_encontrados conta todas as correspondências descobertas, inclusive
  candidaturas mais caras que a escolhida. No modo nome retornar somente o primeiro
  arquivo da pasta objetivo selecionada; conteúdo mantém os correspondentes.
  arquivos_lidos permanece zero por nome e custo_g é zero sem resultado.
- Empates seguem a ordem de inserção. Visitas usam realpath e não seguem symlinks.
  Não são necessárias relaxações numa árvore sem links; cada pasta tem um único pai.

## Contratos de busca por conteúdo (etapa 3)

- BFS, DFS, UCS e A* aceitam modo="nome" (padrão compatível) ou modo="conteudo".
  O CLI oferece --modo nome|conteudo e o menu pergunta qual modo usar.
- Considerar texto as extensões declaradas em EXTENSOES_TEXTO, incluindo textos,
  fontes, CSV/TSV, JSON/JSONL, LOG, XML/HTML/SVG, YAML e configurações, sem distinguir
  maiúsculas. A classificação é por extensão, sem tentativa de detectar MIME.
  Office, ZIP, imagens binárias e extensões desconhecidas não são decodificados.
  PDF usa o extrator opcional isolado em funcoes/pdf.py, nunca UTF-8 bruto.
- No modo nome, aceitar qualquer arquivo regular, independentemente da extensão,
  incluindo PDF/Office/ZIP e arquivos sem extensão. Todas as buscas percorrem
  subpastas; buscas com alvo encerram na pasta objetivo. Somente o modo de
  mapeamento BFS/DFS da etapa 1 percorre todos os arquivos. Conteúdo de Office
  e OCR permanecem sem implementação.
- Ler cada arquivo elegível uma vez com open em texto, encoding="utf-8",
  errors="ignore" e newline="", em blocos de 64 Ki caracteres. Após consumir EOF,
  buffer.tell() fornece bytes reais consumidos desde o início, inclusive
  sequências inválidas e CRLF, sem stat().st_size ou segunda leitura.
- Comparar conteúdo e termo com casefold, como na busca por nome. Ler a pasta
  inteira mesmo após um alvo encontrado; custo local soma todos os textos dela,
  inclusive os que não contêm o termo. Pastas sem textos têm custo local zero.
- arquivos_lidos conta textos efetivamente lidos na exploração inteira (vazios
  também); custo_g soma bytes somente no caminho do resultado. Sem resultado,
  custo_g continua zero. itens_examinados ainda inclui arquivos não textuais.
- Reutilizar examinar_arquivos entre as buscas, evitando diferenças na contagem.
  UCS mantém os limites inferiores e candidaturas, agora com custos em bytes.
- validar_busca é a entrada comum das buscas públicas: exige alvo str não vazio,
  valida o modo e retorna o termo com casefold. Validar também no A* antes de
  preparar bigramas. Motores privados recebem o termo já validado/normalizado;
  tipos inválidos devem produzir ValueError antes de acessar a árvore.
- Ler sempre até EOF mesmo após encontrar o termo, preservando custo integral.
  TextIOWrapper preserva caracteres UTF-8 entre leituras. Guardar até len(termo)-1
  caracteres após casefold para encontrar termos que atravessam blocos, inclusive
  quando casefold expande caracteres. Memória O(tamanho_bloco + len(termo)),
  sem cache entre arquivos ou execuções.
- Após encontrar a correspondência, liberar a janela de comparação (cauda/texto)
  imediatamente e continuar só a leitura, para não reter uma janela longa até EOF.

## Revisão e justificativas de arquitetura

- O timer mede o tempo decorrido da chamada inteira de busca: validações,
  inicialização, listagem/ordenação, leituras/extração, fronteira, heurística,
  métricas e captura de rastro quando solicitada. Inclui espera por E/S e pelo
  escalonador; não representa CPU isolada nem tempo exclusivo de leitura de disco.
- Seleção da função, menu, impressão, montagem/validação dos registros, JSON,
  Markdown e execução do perfil de memória ficam fora do intervalo cronometrado.
  A importação opcional de PDF já ocorre antes das medições.
- _medir_lote centraliza a coordenação, reutilizada por executar e executar_etapa.
  Todos os tempos precedem todos os perfis, evitando intercalar execuções com
  tracemalloc nas amostras. Montar registros somente ao terminar o lote validado.
  Resultados, contadores e rastros das duas execuções devem coincidir.
- Uma amostra por algoritmo em ordem fixa (BFS/DFS/UCS/A* ou subconjunto da etapa).
  Não limpar cache do sistema; os algoritmos seguintes ainda podem encontrar
  dados aquecidos. Tempos não provam superioridade geral nem representam um
  benchmark estatístico. Preservar essa limitação na documentação e relatórios.
- Validar os componentes originais do caminho antes de normalizar: abspath
  apagaria 'link/..' antes de verificar links. validar_caminho mantém os componentes
  e as chamadas ao sistema preservam os erros de caminhos inexistentes.
- A verificação de symlinks é adequada à árvore didática estática, sem garantia
  contra troca concorrente de entradas entre a verificação e a abertura.
- Ordenar a lista no próprio lugar evita alocar outra lista de referências.
- BFS/DFS encerram após examinar a pasta objetivo, antes de calcular realpaths
  dos filhos que não serão explorados; isso preserva a definição de descoberta.
- Separar leitura/listagem, políticas de fronteira, medição e interface facilita
  testar custos e algoritmos sem executar menu ou instrumentação obrigatória.
- Manter testes com oráculos de custos e leitura integral independentes da busca,
  e casos de fronteira para UTF-8, CRLF, casefold, termos longos, symlinks e erros.
  Executar todos com python3 -m tests, sem usar python -O (assert seria removido).
- A revisão foi entregue separadamente. A continuação autorizada inclui agora
  A*, heurística, persistência e relatórios; manter o histórico atualizado.

## Contratos de A* e heurística

- Usar Jaccard de conjuntos de bigramas após casefold. Para um único caractere,
  usar o próprio caractere como token; dois textos vazios têm similaridade 1.
- Alfa padrão 1, finito e não negativo; rejeitar NaN, infinitos e pesos negativos.
  Sua escala acompanha a unidade do custo (itens ou bytes), sem conversão automática.
- Pré-calcular bigramas do termo uma vez por busca. Usar somente o nome da pasta
  (basename), sem listar antecipadamente ou acessar conteúdo para calcular h.
- Compartilhar o motor de heap com UCS em _buscar_prioridade. Manter g separado
  de f no nó para não somar heurística ao custo real. Pastas pendentes usam
  g_pai+h(pasta); expansão revela custo local e candidaturas recebem g_exato, h=0.
  Isso adapta a avaliação adiada de UCS à heurística, sem abertura gratuita.
- Alfa zero desativa estimador e reproduz UCS inclusive desempates e contagens.
- A* não garante ótimo, redução de pastas abertas ou tempo menor. A heurística
  orienta a ordem, sem descartar permanentemente pastas por nomes pouco similares.
  Sem objetivo, todas as pastas acessíveis são examinadas. Documentar isso e o
  contraexemplo testado de caminho mais caro na justificativa de arquitetura.

## Contratos de persistência e relatórios

- A interface salva JSON em resultados/ por padrão, após ambas as medições.
  A pasta é criada sob demanda e ignorada por inteiro pelo Git; não manter
  placeholder ou artefatos gerados na estrutura versionada. Arquivos anteriores
  foram arquivados fora do projeto, conforme docs/VALIDACAO_DOCENCIA.md.
  executar() continua sem persistência para uso isolado e testes. --sem-salvar
  desativa gravação; --resultados seleciona o diretório. Não salvar busca com erro.
- Esquema versao=1: instante_utc, parametros (raiz, alvo, algoritmo, modo, alfa,
  extensoes_texto, extrator_pdf),
  encontrados (caminhos retornados) e metricas (todos os campos de Metricas).
  Alfa é null fora de A*. Preservar Unicode e rejeitar NaN/Infinity na serialização.
- Campo opcional medicao documenta métodos (perf_counter/tracemalloc), unidades
  (ms/KiB), execuções separadas e contadores de uma execução. Validar metadados
  presentes para não apresentar outra instrumentação como tracemalloc. Registros
  v1 antigos sem esse campo permanecem compatíveis com o contrato original.
- Campo opcional protocolo_lote=tempos_antes_dos_perfis_memoria registra a ordem
  das fases nas etapas. Validar quando presente e agrupar protocolos diferentes
  separadamente. Ausência em JSON antigo significa ordem não registrada, sem
  atribuir retroativamente o protocolo novo às medições anteriores.
- extensoes_texto registra a lista ordenada efetivamente usada no modo conteúdo,
  null no modo nome. Campo adicional opcional compatível com JSONs v1 antigos;
  ausência aparece como "não registrado" no relatório, sem inventar configuração.
- extrator_pdf identifica pypdf/versão ou indisponível; campo opcional para aceitar
  JSONs anteriores. Comparativos separam versões/políticas diferentes.
- avaliacao_final é {g, h: 0, f: g} para objetivo confirmado UCS/A*, ou null.
  Compatível com registros antigos sem o campo; f final pode ser derivado de g.
- Usar criação exclusiva ('x'), nomes com time_ns, pid e contador de colisão.
  Não sobrescrever execuções anteriores; remover arquivo parcial se escrita falhar.
  Não há garantia de transação em queda abrupta do processo ou do sistema.
- Relatórios leem arquivos ou diretórios JSON sem executar buscas; validar
  versão, campos e números finitos não negativos. Erros incluem caminho do JSON.
  Não ignorar silenciosamente JSON corrompido; rejeitar diretório sem registros.
- Remover entradas duplicadas por realpath. Não seguir arquivos JSON symlink em
  diretórios e rejeitar entrada explicitamente symlink. Ordem estável por nome.
- Separar parâmetros e métricas em tabelas vinculadas por ID; distinguir quantos
  arquivos foram retornados das correspondências descobertas na exploração.
  Mostrar unidade de g e escapar pipes, HTML e quebras de linha nos valores.
- Saída opcional .md; rejeitar destino symlink e extensão diferente. Sem --saida,
  imprimir Markdown. Artefatos gerados JSON/Markdown em resultados/ são ignorados.
- Comparar somente mesma raiz, alvo, modo e configuração de extensões; manter diretório de resultados fora
  da raiz buscada para as gravações não alterarem a árvore entre comparações.

## Tabela comparativa da etapa 3

- main.py --comparar executa UCS e A* por conteúdo, sequencialmente, com alvo
  padrão algoritmo; usa o mesmo estado inicial e medições independentes.
- Mostrar exatamente: Algoritmo, Palavra no Conteúdo, Caminho, Pastas Abertas,
  Arquivos Lidos do Disco, Custo Total f(n), Tempo (ms).
- Acrescentar a tabela de Métricas principais com N, itens, leituras, g, pico
  tracemalloc e tempo. A tabela original não substitui a instrumentação obrigatória.
- f(n)=g(n)+h(n); UCS usa h=0 e candidaturas objetivo confirmadas de A* usam h=0.
  Portanto f final=g, em bytes, sem somar a heurística do nome ao custo final.
  Ausência de resultado aparece como Não encontrado e f=—, sem ótimo fictício zero.
- Caminho é o arquivo encontrado; múltiplos arquivos da mesma pasta usam quebras
  escapadas na célula. Raiz, extensões e versão PDF formam grupos separados.
- Arquivos Lidos do Disco é o contador de arquivos abertos/lidos pela aplicação,
  não contagem de operações físicas de disco. Cache pode atender essas leituras.
- Relatório geral inclui a tabela para conteúdo/algoritmo. --comparativo no
  conversor produz somente essa tabela; --alvo seleciona outro termo, se desejado.

## Extração PDF

- fontTools consta apenas como melhoria futura na seção 5.1 de docs/ARQUITETURA.md.
  A proposta não indica instalação nem benefício já validado. Preservar a
  distinção entre decodificação de fontes e OCR e conferir compatibilidade de
  versões, fidelidade do texto e custos antes de eventual incorporação.
- Carregar a dependência opcional antes das medições, evitando cobrar importação
  só de UCS. Falta de pypdf só impede ler conteúdo de PDF, com erro orientativo.
- Cada PDF é aberto uma vez por expansão e todas as páginas são extraídas, mesmo
  após encontrar o termo; comparar casefold e inserir quebra ENTRE páginas,
  nunca uma quebra artificial após a última. A busca equivale a unir os textos
  extraídos com '\n', preservando quebras já devolvidas pelo extrator. Liberar
  a janela de comparação por página, mantendo somente a cauda necessária.
- Contar bytes entregues ao parser por read/readline/readinto, inclusive após
  seek e releituras; não usar filesize como aproximação. g soma esse custo local
  com os bytes de textos no caminho. arquivos_lidos conta o PDF uma vez.
- PDF tem busca/decodificação própria; a garantia de memória em blocos vale para
  texto simples, não para as estruturas internas de pypdf.
- Não executar OCR. PDF só imagem pode não ter texto extraível; PDF protegido ou
  corrompido deve gerar erro com caminho, sem produzir falso resultado completo.

## Entregas completas por etapa

- A raiz vem de --raiz ou da interface de pastas. No menu e nas flags de seleção,
  restaurar o último caminho válido; CLI direta sem seletor mantém o padrão
  ./docencia/fontes quando --raiz é omitido. Caminhos relativos usam o diretório
  de trabalho. Preservar os dados de entrada e distinguir o acervo real da árvore
  gerada; ../Docencia/Fontes é o acervo real ao executar da pasta do projeto.
- --etapa 1 executa somente BFS/DFS em mapeamento. --etapa 2 compara BFS/DFS/UCS/A*
  por nome, alvo padrão livro. --etapa 3 compara UCS/A* por conteúdo, alvo padrão
  algoritmo; --comparar é atalho da etapa 3. Menu oferece as três entregas além
  das buscas individuais. Rejeitar opções incompatíveis; global não recebe alvo.
- Executar tempo e memória com rastros separados; comparar também os rastros e
  só então publicar. O custo de manter o rastro entra nas medições das etapas.
- JSON v1 acrescenta parametros.escopo (mapeamento/objetivo), etapa, base_caminhos,
  experimento comum a cada lote e expansoes [{diretorio, custo_local, g}]. Etapa 1
  usa alvo null e primeiros_10 como projeção ordenada de encontrados. Compatibilidade
  de registros antigos sem os novos campos preservada.
- Validar rastro: tamanho=N, pai anterior ao filho, diretórios sem repetição,
  g=valor do pai+custo local, g final compatível com a pasta do objetivo.
- Etapa 1 registra cronologia completa dos arquivos, primeiros 10 lado a lado,
  totais e sequência das expansões. g objetivo não se aplica ao mapeamento.
- Nos primeiros 10, exigir no máximo um BFS e um DFS por grupo/experimento.
  Rejeitar duplicatas com indicação para selecionar um JSON por algoritmo;
  não sobrescrever silenciosamente uma cronologia ao montar as colunas.
- Etapa 2 mostra os quatro algoritmos, alvo, primeiro caminho, N, g, tempo/memória
  e análise da soma de custos em cada diretório do caminho, sem relistar pastas.
- Relatórios exibem caminhos completos relativos à base registrada (./docencia/...
  no uso padrão). KB nas tabelas acadêmicas é decimal, convertido de KiB;
  as métricas principais mantêm tracemalloc em KiB.
- Etapas 2/3 demonstram redução ou aumento de N/leituras e, com rastro disponível,
  mostram diretórios abertos por UCS e não abertos por A*. Isso é economia
  observada pela parada antecipada, não poda permanente por prova de irrelevância.
- Agrupar relatórios por experimento/raiz/política para não misturar amostras.
  JSONs são exclusivos; cada execução de etapa atualiza seu etapa_N.md.

## Seleção de pastas e preferências

- funcoes/pastas.py concentra seleção, navegação e preferência; executar e
  executar_etapa permanecem sem interface e sem persistir preferências.
- macOS usa choose folder por /usr/bin/osascript, com caminho em argv, sem shell;
  outras plataformas usam askdirectory com importação tardia de tkinter.
  Indisponibilidade gráfica oferece navegação no terminal; cancelamento não
  substitui a pasta anterior. A aplicação aguarda o diálogo de forma síncrona.
- Menu 8 seleciona pasta, menu 9 navega por nomes/tipos. A navegação não abre
  conteúdos, segue as regras de symlinks e permite subpastas, pai, caminho manual
  e sugestão de nome de arquivo. A sugestão mantém a busca parcial por nome;
  --alvo explícito prevalece e conteúdo/mapeamento não usam nome como termo.
- .file_hunter.json local, ignorado pelo Git, guarda versao=1 e ultimo_caminho
  absoluto. --config seleciona outro JSON; --sem-salvar controla só resultados.
  Validar esquema, pasta e symlinks, usar temporário exclusivo e os.replace.
  Avisar sobre configuração inválida ou falha de gravação sem interromper busca.
- Seleção, leitura/escrita de preferência e prévia de diretórios são ações da
  interface fora das medições. Não fornecer listagens ou custos da prévia aos
  algoritmos; cada busca lista novamente e contabiliza suas próprias expansões.
- Base consultada: Binary-Search-Tree do usuário, revisão 990e4a93684820bd8464b56cc66345ac74302056.
  Adaptar apenas padrões de menu e JSON, preservando a proibição de classes BST,
  ausência de Matplotlib e compatibilidade com o ambiente Python 3.9.
