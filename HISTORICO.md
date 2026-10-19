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

## 6. Heurística e A* — entrega atual — progresso estimado 86%

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

## Pendências

- Salvar execuções em JSON em resultados/ e convertê-las para tabelas Markdown.
- Consolidar justificativa final da arquitetura e instruções de comparação.
- Manter limites explícitos: árvore estática durante medições, texto por extensão,
  memória medida de alocações Python e A* sem garantia de ótimo ou economia.
