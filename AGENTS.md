# File Hunter Agent

## Escopo e dependências

- Implementar por etapas. Passo A concluído; continuação autorizada pelo usuário.
  Entrega atual: BFS/DFS e UCS por nome e conteúdo, menu e argumentos.
- Usar apenas biblioteca padrão do Python 3: collections, heapq, os, time,
  tracemalloc, json e argparse; dataclasses é necessário para a dataclass exigida.
- Não reutilizar classes de BST. O nó é um diretório.
- Matplotlib somente em eventual módulo opcional de visualização, nunca nas buscas
  ou métricas; não instalar dependências para o passo A.

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
   execução; não reutilizar visitados ou métricas entre medições.
9. Heurística futura: h(n) = alfa * (1 - similaridade(nome_pasta, termo)), com
   Jaccard de bigramas ou Levenshtein normalizado. Não é admissível; A* não
   garante caminho ótimo.

## Contratos do passo A

- listar_dir retorna uma lista de os.DirEntry ordenada por nome. Exclui links
  simbólicos e entradas que não são arquivos regulares nem diretórios. Não abre
  uma raiz que seja symlink e rejeita componentes simbólicos no caminho.
- Erros de acesso e caminhos ausentes são propagados ao chamador.
- Métricas de contagem são atualizadas pelas buscas futuras, não pela listagem.
- custo_g é o custo acumulado do caminho, não o custo de toda a exploração.
- Tempo é expresso em ms; pico de memória em KiB (campo pico_mem_kb).
- O gerador usa seed fixa 2024 e um gerador congruencial próprio. Reexecutá-lo
  sobrescreve apenas seus arquivos conhecidos, sem apagar outros arquivos.

## Contratos de BFS e DFS

- Encerrar após a primeira pasta que contenha correspondências; retornar todos
  os arquivos correspondentes dessa listagem completa. arquivos_encontrados é
  a quantidade de correspondências, itens_examinados conta a listagem inteira.
- Acumular g incluindo a listagem da raiz e da pasta do resultado. Sem resultado,
  custo_g permanece zero. arquivos_lidos permanece zero na busca por nome.
- Ordem alfabética de expansão para irmãos, inclusive DFS (empilhamento inverso).
- Marcar realpath ao inserir na fronteira; usar uma única fronteira deque e
  compartilhar a lógica de expansão entre BFS e DFS para manter a descoberta igual.
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
- Heap contém sempre (prioridade, contador, nó). Nó é (pasta, None) para uma
  expansão ou (pasta, correspondências) para uma candidatura já expandida.
  Remover candidatura não conta como nova expansão e não relista a pasta.
- arquivos_encontrados conta todas as correspondências descobertas, inclusive
  candidaturas mais caras que a escolhida. Retornar os arquivos da pasta objetivo
  selecionada. arquivos_lidos permanece zero e custo_g é zero sem resultado.
- Empates seguem a ordem de inserção. Visitas usam realpath e não seguem symlinks.
  Não são necessárias relaxações numa árvore sem links; cada pasta tem um único pai.

## Contratos de busca por conteúdo (etapa 3)

- BFS, DFS e UCS aceitam modo="nome" (padrão compatível) ou modo="conteudo".
  O CLI oferece --modo nome|conteudo e o menu pergunta qual modo usar.
- Considerar texto as extensões .txt, .md e .py, sem distinguir maiúsculas.
  A classificação é por extensão, sem tentativa de detectar MIME. Não ler .png
  ou extensões desconhecidas. Novas extensões exigem alterar EXTENSOES_TEXTO.
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
- Ler sempre até EOF mesmo após encontrar o termo, preservando custo integral.
  TextIOWrapper preserva caracteres UTF-8 entre leituras. Guardar até len(termo)-1
  caracteres após casefold para encontrar termos que atravessam blocos, inclusive
  quando casefold expande caracteres. Memória O(tamanho_bloco + len(termo)),
  sem cache entre arquivos ou execuções.

## Revisão e justificativas de arquitetura

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
- Revisão não autoriza antecipar A*, heurística ou relatórios. As justificativas
  serão consolidadas na documentação final quando esses módulos forem entregues.
