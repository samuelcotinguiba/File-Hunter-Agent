# File Hunter Agent

Projeto didático em Python 3 para comparar buscas em árvores de diretórios.
Somente o passo A está implementado: estrutura, listagem segura, métricas e
gerador de dados. BFS, DFS, UCS, A*, menu e relatórios aguardam as próximas etapas.
Não há dependências externas. `dataclasses`, da biblioteca padrão, exige Python
3.7 ou posterior.

Execute a partir de `File-Hunter-Agent/`:

```sh
python3 gerar_arvore.py
python3 -c 'from funcoes.listagem import listar_dir; print([e.name for e in listar_dir("docencia/fontes")])'
```

O gerador cria 40 pastas abaixo de `docencia/fontes/`, com profundidade máxima
de quatro níveis e 64 arquivos .txt, .md, .py e .png. A seed é 2024. Apenas parte
dos arquivos de texto contém `algoritmo`. A árvore gerada e os JSON de execuções
são ignorados pelo Git. Novas execuções sobrescrevem os arquivos conhecidos.

`listar_dir(caminho)` retorna `os.DirEntry` ordenados por nome, sem links
simbólicos. Erros de acesso são propagados. A listagem não atualiza contadores.
`Metricas` guarda contadores e custo; `medir_tempo` e `medir_memoria` retornam
`(resultado, medição)`. Execute cada auxiliar com estado novo e separado.

## Estruturas de dados e justificativas de design

- **Nó e expansão:** diretório; uma chamada de listagem representa uma expansão.
- **Listagem:** `os.scandir`, ordenação por nome e exclusão de symlinks.
- **Métricas:** dataclass com valores iniciais zero; tempo e memória separados.
- **BFS e DFS:** a implementar; deque para fila/pilha.
- **UCS e A*:** a implementar; heap com prioridade, contador e nó.
- **Ciclos:** a implementar nas buscas com conjunto de realpaths visitados.
- **Custos e heurística:** definições registradas no AGENTS.md; heurística futura
  não admissível, sem garantia de caminho ótimo para A*.
- **Relatórios:** a implementar; JSON e tabelas Markdown.
