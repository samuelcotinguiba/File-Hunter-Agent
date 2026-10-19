# Desenvolvimento, objetivos e estado da entrega

[Pasta de documentação](./) · [Apresentação do projeto](../README.md)

## 1. Problema e objetivos

O objetivo geral consiste em analisar como a política de exploração influencia
a descoberta de arquivos e o trabalho realizado sobre o sistema de arquivos.
Os objetivos específicos são:

1. Comparar a ordem de descoberta de BFS e DFS em um mapeamento integral.
2. Comparar quatro estratégias para localizar um termo no nome de um arquivo.
3. Investigar o efeito de uma heurística lexical na busca por conteúdo.
4. Registrar métricas verificáveis e relatórios reproduzíveis por etapa.
5. Justificar as estruturas de dados e os compromissos da implementação.

O nó de busca corresponde a um diretório. Sua expansão consiste em listar o
conteúdo com `os.scandir`; um arquivo é descoberto quando aparece na expansão
do diretório pai. A correspondência usa substring após `casefold`, sem distinção
entre maiúsculas e minúsculas. Não há classes de árvore binária de busca ou modelos
de aprendizado de máquina. Matplotlib é um extra opcional da visualização;
as buscas e a instrumentação usam a biblioteca padrão e o adaptador PDF autorizado.

O mapeamento completo é exclusivo de BFS/DFS na etapa 1. As demais tarefas são
orientadas ao objetivo, embora possam explorar toda a árvore quando necessário.
As condições de correção pressupõem uma árvore finita, acessível e estática.

## 2. Processo de construção

O projeto foi construído incrementalmente, com verificações executáveis e registro
das decisões em [AGENTS.md](AGENTS.md) e [HISTORICO.md](HISTORICO.md):

1. **Modelagem e base:** definimos diretório como nó, expansão por `os.scandir`,
   descoberta no pai, exclusão de symlinks e campos da dataclass de métricas.
   Criamos o gerador determinístico para comparar estratégias sobre os mesmos dados.
2. **Busca cega:** implementamos BFS/DFS com deque e verificamos a ordem de visita,
   a descoberta dos arquivos e a separação entre mapeamento completo e busca com alvo.
3. **Custo uniforme:** acrescentamos UCS com heap e avaliação adiada, pois o custo
   em itens só é conhecido ao abrir a pasta. Testes com objetivos mais baratos
   conferiram a seleção por custo acumulado e os desempates.
4. **Conteúdo, heurística e formatos:** centralizamos a leitura em blocos e o
   custo em bytes; A* reutilizou o motor de heap com Jaccard de bigramas. Testes
   demonstraram economia e um contraexemplo de ótimo. Depois, a extensão PDF
   autorizada foi isolada em um adaptador, com limitações explícitas sem OCR.
5. **Instrumentação e entregas:** separamos as chamadas de tempo e memória,
   conferimos sua equivalência e produzimos JSONs auditáveis e tabelas por etapa.
   Impressão e persistência ficaram fora do cronômetro.
6. **Validação e revisão:** usamos cenários com custos conhecidos, oráculos
   independentes e o acervo real de 62 PDFs. Na consolidação, unificamos o percurso
   BFS/DFS, removemos listas temporárias e corrigimos a validação de alvos na API.
   Oito percursos preservaram resultados, contadores e rastros antes/depois.
7. **Seleção de dados:** adaptamos os padrões de menu e persistência do projeto
   Binary-Search-Tree do usuário para oferecer seletor nativo, navegação pelo
   terminal e restauração da última pasta em JSON. A seleção ocorre antes das
   medições; os motores de busca continuam síncronos e independentes da interface.
8. **Visualização dos resultados:** acrescentamos Matplotlib sob demanda para
   exportar seis métricas em PNGs a partir dos JSONs existentes. O padrão de aviso
   de instalação foi adaptado do projeto de referência; os gráficos não repetem
   buscas nem dependem das classes BST. Os testes verificam ausência do extra,
   agrupamento, valores representados, exportação e tratamento de falhas.

As justificativas e os compromissos de cada decisão estão na
[síntese da arquitetura](ARQUITETURA.md#31-síntese-das-decisões-de-arquitetura).
A [metodologia](METODOLOGIA.md#74-verificação-da-revisão-de-código) registra
a comparação local de memória da revisão; os tempos históricos do acervo real
continuam vinculados à revisão identificada no relatório original.

## 3. Estado funcional e interpretação dos percentuais

| Componente | Implementação verificada |
| --- | ---: |
| Base, gerador e listagem | 100% |
| Etapa 1 — BFS/DFS e cronologia global | 100% |
| Etapa 2 — Quatro estratégias e busca por nome | 100% |
| Etapa 3 — Conteúdo e comparação UCS/A* | 100% |
| Interface, persistência e relatórios | 100% |
| Extra opcional de gráficos comparativos | 100% |

Os percentuais indicam funcionalidades implementadas e verificadas segundo o
escopo informado. Não medem cobertura de testes, ausência de defeitos ou aprovação
docente. O histórico registra as correções e as limitações identificadas.

## 4. Evidências e continuidade

A [metodologia](METODOLOGIA.md) reúne métricas, cenários com e sem economia de
leituras e as limitações experimentais. A [validação do acervo real](VALIDACAO_DOCENCIA.md)
registra os resultados obtidos com os 62 PDFs. A [arquitetura](ARQUITETURA.md)
apresenta a fórmula de h, a avaliação adiada de g, os motores compartilhados e
a justificativa da execução síncrona. O extra de gráficos pode instalar fontTools;
avaliar sua influência específica nos PDFs continua proposto na seção 5.1 desse
documento, sem alterar os resultados históricos.

O [histórico](HISTORICO.md) mantém a sequência das entregas e suas verificações.
As evidências numéricas permanecem associadas à revisão que as produziu; mudanças
de organização documental não representam novos experimentos.
