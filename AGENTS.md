# File Hunter Agent

## Escopo e dependências

- Implementar por etapas. Passo A concluído; continuação autorizada pelo usuário.
  Entrega atual: BFS/DFS por nome, menu e argumentos básicos.
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
  igual ao da execução de tempo; divergência indica árvore alterada entre chamadas.
