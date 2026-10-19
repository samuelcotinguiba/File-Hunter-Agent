# Guia de manutenção — File Hunter Agent

Este arquivo orienta alterações no projeto; a execução do Python não depende
dele. Reúne os contratos essenciais, enquanto as justificativas completas ficam
na documentação específica. Caminhos citados como `docs/...` são relativos à raiz.

## Escopo e dependências

- As três etapas estão implementadas. Preservar suas entregas e atualizar
  [HISTORICO.md](HISTORICO.md) com mudanças, verificações e limitações.
- O núcleo usa a biblioteca padrão, incluindo dataclasses. As exceções
  autorizadas são pypdf para PDFs e Matplotlib para gráficos, com suas dependências
  transitivas, reunidas em um único `requirements.txt`. Instalar somente na `.venv`
  e preservar o carregamento opcional desses recursos no código.
- Matplotlib é importado sob demanda em `funcoes/visualizacao.py`; buscas e
  instrumentação não dependem dele. Informar instalação ao solicitar gráficos
  sem a dependência. A instalação pode acrescentar fontTools ao ambiente;
  sua influência na extração PDF exige validação própria.
- Seleção de pastas usa subprocess no macOS e tkinter opcional nas demais
  plataformas, ambos da biblioteca padrão. Sem novas dependências de interface.
- Não reutilizar classes BST. As buscas permanecem síncronas e sequenciais.

## Decisões de design

1. Nó = diretório. Expandir = listar com `os.scandir`; conta como uma pasta aberta.
2. Arquivo é descoberto quando aparece na expansão do pai, igualmente em BFS/DFS.
3. Etapa 2: g(n) soma itens elegíveis (arquivos + subpastas) de cada diretório
   no caminho, incluindo raiz e objetivo. Nome contém o termo com `casefold`.
4. Etapa 3: g(n) soma bytes efetivamente lidos no caminho. Objetivo é termo no
   conteúdo, com `casefold`; textos usam UTF-8 e `errors="ignore"`. PDF é isolado
   no adaptador opcional, sem OCR ou suporte a conteúdo de Office.
5. Visitados guardam `realpath`; nunca seguir symlinks, inclusive na raiz.
6. Heap contém `(prioridade, contador, nó)` para desempate estável.
7. BFS usa `deque.popleft()`; DFS usa `deque.pop()` com filhos em ordem inversa
   de inserção para expandir irmãos alfabeticamente.
8. Tempo usa `time.perf_counter` em ms; memória usa pico `tracemalloc` em KiB,
   em chamadas separadas e com estado novo. Nos lotes, todos os tempos precedem
   todos os perfis. Comparar resultados, contadores e rastros entre as chamadas.
9. h(n) = alfa × (1 − Jaccard dos bigramas do nome da pasta e do termo).
   Alfa é finito e não negativo; alfa zero reproduz UCS. A heurística não é
   admissível: A* não garante ótimo, economia ou descarte permanente de pastas.

## Invariantes de implementação

- `listar_dir` retorna entradas regulares ordenadas e propaga erros. Validar
  componentes do caminho antes de normalizá-lo, preservando a rejeição de links.
- Mapeamento completo é exclusivo de BFS/DFS na etapa 1, sem alvo ou conteúdo.
  As etapas 2 e 3 procuram um objetivo; podem explorar tudo quando necessário.
- BFS/DFS compartilham `_percorrer`; UCS/A* compartilham `_buscar_prioridade`.
  Manter g separado de f e os contadores comuns às estratégias.
- O custo local só é conhecido após expansão contabilizada. UCS usa g do pai
  como limite inferior e candidaturas com g exato; A* acrescenta h às expansões
  pendentes. Objetivo confirmado usa h=0 e f=g. Sem resultado, g=0 é convenção;
  apresentar custo indisponível, inclusive nos gráficos.
- Ler todos os arquivos elegíveis da pasta até o final, mesmo após encontrar
  o termo. Texto em blocos preserva correspondências entre blocos; PDF percorre
  todas as páginas e conta bytes entregues ao parser, inclusive releituras.
- g representa o caminho final; N, itens e leituras contam toda a exploração.
  Não chamar leituras da aplicação de operações físicas nem pico tracemalloc de RSS.
- Seleção, preferências, impressão, JSON, Markdown e gráficos ficam fora das
  medições. Não reutilizar prévias, caches de conteúdo ou custos entre buscas.
- Preservar o esquema JSON v1 e seus campos opcionais. Validar antes de relatar;
  não ignorar corrupção ou misturar experimentos/políticas. Evitar sobrescritas
  e remover arquivos parciais em falha. `resultados/` é criado sob demanda e ignorado.
- Gráficos consomem registros existentes, separam grupos compatíveis e usam
  PNG/Agg sem janela. Não substituir relatórios nem repetir buscas para desenhar.
- Preservar os acervos de entrada. O gerador didático usa seed 2024 e sobrescreve
  somente seus arquivos conhecidos; resultados devem ficar fora da raiz buscada.
- A raiz explícita prevalece. Menu/seletores restauram a última pasta válida em
  `.file_hunter.json`; CLI direta sem seleção mantém `./docencia/fontes`.
  Preferência é independente de `--sem-salvar`; cancelamento preserva a anterior.
- Rejeitar opções incompatíveis antes de abrir diálogos. Testes de interface
  simulam seletor e entrada; não abrir janelas na suíte.
- `interface.py` guia as três etapas e oferece retorno/continuação por laços.
  Preservar pasta e termos na sessão; CLI direta não recebe perguntas de retorno.
  Gráficos/relatório usam os resultados atuais sem repetir buscas. O resumo do
  terminal preserva a entrega completa em JSON/Markdown; progresso fica fora das medições.

## Verificação e documentação

- Executar testes pertinentes e `python3 -m tests` para alterações no código;
  usar também `.venv/bin/python -m tests` para os extras instalados. Não usar `-O`.
- Conferir links locais/âncoras e `git diff --check` nas mudanças documentais.
- O [README principal](../README.md) é o único resumo e aponta para [docs/](./).
  Manter este guia apenas em `docs/AGENTS.md`, sem README adicional nessa pasta.
- [USO.md](USO.md): ambiente, comandos, seleção e preferências.
- [ARQUITETURA.md](ARQUITETURA.md): contratos detalhados, módulos e justificativas.
- [METODOLOGIA.md](METODOLOGIA.md): métricas, tabelas, protocolo e rastreabilidade.
- [VALIDACAO_DOCENCIA.md](VALIDACAO_DOCENCIA.md): resultados históricos e PDFs reais.
- [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md): construção e estado funcional.
- Descrever observações, garantias condicionais e trabalhos futuros separadamente.
  Não atribuir ganhos não medidos; registrar ambiente e limitações de reprodução.
