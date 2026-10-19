# Documentação completa — File Hunter Agent

[Resumo do projeto](../README.md)

Esta pasta concentra a documentação detalhada e o histórico versionado.
O README da raiz apresenta o resumo e os comandos iniciais; os documentos abaixo
explicam uso, arquitetura, experimentos, decisões e evolução.

| Documento | Conteúdo |
| --- | --- |
| [Guia de uso](USO.md) | Ambiente, escolha da pasta, menu, argumentos, etapas, resultados e relatórios. |
| [Arquitetura](ARQUITETURA.md) | Modelo de diretórios, módulos, estruturas, g/h/f, execução síncrona e justificativas. |
| [Metodologia](METODOLOGIA.md) | Métricas, protocolo, tabelas comparativas, testes, reprodução e limites. |
| [Validação com Docencia/Fontes](VALIDACAO_DOCENCIA.md) | Resultados do acervo real e limitações dos PDFs. |
| [Desenvolvimento](DESENVOLVIMENTO.md) | Objetivos, construção por etapas e estado funcional da entrega. |
| [Histórico](HISTORICO.md) | Mudanças, decisões e verificações por entrega. |

## Como consultar

1. Para executar em outra pasta, consulte a [seleção da raiz](USO.md#2-como-a-pasta-é-escolhida).
2. Para justificar o projeto academicamente, consulte a matriz de decisões da
   arquitetura e o processo de construção descrito no desenvolvimento.
3. Para interpretar os resultados, use as definições e limitações da metodologia.
4. Para acompanhar mudanças, use o histórico junto ao log de commits do Git.

## Documentos e artefatos de execução

Os arquivos desta pasta integram a documentação versionada. JSONs, logs e tabelas
Markdown gerados pelo programa são artefatos locais: `resultados/` é criado
somente quando uma execução solicita gravação e fica ignorado pelo Git.
`--sem-salvar` executa sem criar esses arquivos; `--resultados` muda seu destino.

Os resultados antigos foram arquivados fora da pasta do projeto, com conferência
de hashes e metadados. A localização está na [validação do acervo](VALIDACAO_DOCENCIA.md#6-artefatos-e-reprodução).
Os caminhos antigos do histórico identificam a estrutura usada na época de cada
experimento. Os contratos de manutenção permanecem em [AGENTS.md](../AGENTS.md).
