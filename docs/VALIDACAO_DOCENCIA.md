# Validação com o acervo Docencia/Fontes

[Apresentação](../README.md) · [Metodologia](METODOLOGIA.md)

## 1. Escopo e ambiente

A avaliação utiliza o acervo real em `../Docencia/Fontes`, externo ao diretório
versionado do projeto. A raiz considerada é `Fontes`, conforme o domínio definido
para as buscas. Os arquivos originais não são modificados nem incluídos no Git.

| Característica | Valor observado |
| --- | --- |
| Revisão da implementação | `ef0489a0c9d8e1de89063bcad51925ec773754d5` |
| Python | 3.9.6 |
| Sistema / arquitetura | Darwin / arm64 |
| Extrator | pypdf 6.21.1 |
| Diretórios, incluindo a raiz | 11 |
| Arquivos regulares | 62 PDFs |
| Tamanho armazenado | 428.430.326 bytes, aproximadamente 428,43 MB decimais |
| Links simbólicos identificados | 0 |
| Alvo da etapa 2 | `livro` |
| Alvo da etapa 3 | `algoritmo` |
| Alfa no A* | 100 |

O inventário de caminhos, tamanhos e timestamps foi salvo antes das buscas.
As etapas 1/2 precederam a auditoria integral dos PDFs. A etapa 3 é executada
após essa auditoria, com o cache potencialmente aquecido. Cada algoritmo possui
uma amostra temporal e uma execução independente de memória; não há inferência
estatística de superioridade.

## 2. Mapeamento global — etapa 1

| Algoritmo | Pastas abertas | Itens examinados | Arquivos encontrados | Arquivos lidos | Tempo (ms) | Pico (KiB) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BFS | 11 | 72 | 62 | 0 | 0,906 | 19,961 |
| DFS | 11 | 72 | 62 | 0 | 0,884 | 16,328 |

O conjunto de arquivos retornados foi comparado com uma enumeração independente
do acervo. Ambos os algoritmos cobriram os mesmos 62 PDFs. Os primeiros dez
arquivos coincidem, pois a diferença de profundidade ocorre posteriormente.
A primeira divergência está na posição 23:

- BFS: `Fontes GTI/LIVRO_UNICO_GTI.pdf`.
- DFS: `Fontes GD/Ferramentas gestao de dados/Documentação+Ciclo+de+vida+na+criação+de+conta.pdf`.

Essa coincidência inicial é uma propriedade do acervo, não uma falha da política
LIFO. As cronologias completas e os percursos foram registrados no relatório.

## 3. Busca por nome — etapa 2

| Algoritmo | Pasta do arquivo retornado | Arquivo | Pastas abertas | g (itens) | Tempo (ms) | Pico (KiB) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| BFS | Fontes DMN | Livro Desenvolvimento Mobile.pdf | 3 | 17 | 0,492 | 9,228 |
| DFS | Fontes DMN | Livro Desenvolvimento Mobile.pdf | 3 | 17 | 0,448 | 9,184 |
| UCS | Fontes GTI | LIVRO_UNICO_GTI.pdf | 10 | 13 | 0,747 | 9,534 |
| A* | Fontes DMN | Livro Desenvolvimento Mobile.pdf | 3 | 17 | 0,431 | 9,692 |

Nenhum conteúdo PDF foi aberto nesta etapa. A raiz contém nove subdiretórios;
o custo do caminho é 9+8=17 em DMN e 9+4=13 em GTI. UCS identificou o menor
custo acumulado, embora tenha expandido mais pastas. A* selecionou um objetivo
de custo maior com menos expansões. O resultado reforça a distinção entre
otimalidade do caminho e trabalho de exploração.

## 4. Auditoria integral de extração

Antes da comparação de conteúdo, cada PDF foi aberto por uma rotina de auditoria
independente do percurso de busca, usando o mesmo parser. O texto de referência
foi composto pela união dos textos extraídos das páginas, com uma quebra entre
elas. Foram preservados somente metadados, contagens e presença do termo; os
conteúdos dos documentos não foram copiados para os relatórios.

| Verificação | Resultado |
| --- | ---: |
| PDFs processados sem exceção | 62 de 62 |
| Páginas examinadas | 7.592 |
| Páginas que forneceram texto não vazio | 6.940 |
| PDFs com algum texto extraído | 55 |
| PDFs sem texto extraído | 7 |
| PDFs cujo texto extraído contém `algoritmo` | 20 |

Os sete arquivos sem texto extraível nesta configuração são:

1. `Fontes BD/sumario-elmasri.pdf`.
2. `Fontes DMN/Desenvolvimento_Mobile_Do_Zero_Ao_Deploy.pdf`.
3. `Fontes DMN/Mobile_Development_Strategy_And_Code.pdf`.
4. `Fontes MD/Aula Inicial Mineração de dados.pdf`.
5. `Fontes PAA/Meta-Heurísticas em Pesquisa Operacional.pdf`.
6. `Fontes UDP/GuiaFigmaIniciantes.pdf`.
7. `Fontes UDP/Implementação de Tendências Modernas de UI-UX com Flutter.pdf`.

Ausência de texto extraído não demonstra ausência visual da palavra. Esses PDFs
não tiveram sua pesquisa visual validada; OCR não faz parte da implementação.
Também foram registrados 3.714 avisos de pypdf sobre a ausência de fontTools para
tratamento completo de determinadas codificações CFF Type1. Esses avisos não
interromperam a leitura, mas limitam afirmações sobre a fidelidade integral da
extração. Nenhuma dependência adicional foi instalada durante a avaliação.

A avaliação futura de fontTools, com sua finalidade, limitações e critérios de
adoção, está documentada na [seção 5.1 da arquitetura](ARQUITETURA.md#51-possível-uso-futuro-de-fonttools).
Trata-se de uma proposta posterior: os resultados desta validação continuam
representando o ambiente sem essa biblioteca, sem pressupor correção dos sete
arquivos sem texto extraído ou melhoria já demonstrada nos demais.

## 5. Busca por conteúdo — etapa 3

As quatro chamadas foram concluídas. Em cada algoritmo, a execução temporizada
e o perfil de memória produziram os mesmos caminhos, contadores e rastro.

| Algoritmo | Pastas abertas | Itens examinados | Correspondências descobertas | Arquivos lidos | g / f final (bytes) | Tempo (ms) | Pico (KiB) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| UCS | 10 | 60 | 19 | 50 | 6.204.185 | 201.669,849 | 299.214,132 |
| A* | 10 | 60 | 19 | 50 | 6.204.185 | 198.947,927 | 299.215,223 |

A* não reduziu expansões ou leituras nesta configuração. A pequena diferença
de tempo é uma observação local, com uma amostra por algoritmo e cache aquecido;
não demonstra superioridade estatística. Os picos correspondem a aproximadamente
292,20 MiB de alocações Python rastreadas. Cada perfil durou cerca de dez minutos;
essa duração não integra o tempo de busca apresentado na tabela.

Ambos retornaram `Fontes PCD/LIVRO SISTEMAS-DIGITAIS.pdf`, cujo nome não contém
`algoritmo`, mas o texto extraído satisfaz o objetivo. A soma de bytes dos ramos
efetivamente expandidos foi 260.270.782; o g final de 6.204.185 corresponde ao
caminho do resultado, e não a esse volume total. A subpasta de ferramentas de GD
e seus 12 PDFs não foram expandidos nas buscas com objetivo. A auditoria completa
permanece uma checagem separada, sem fornecer prioridades previamente às buscas.

Uma agregação independente dos custos obtidos na auditoria indica g mínimo de
**6.204.185 bytes**, na pasta `Fontes PCD`, coincidindo com g das chamadas
temporizadas. Os dados de auditoria não são utilizados para decidir as
prioridades das buscas reais.

Foram conferidos os custos de cada expansão com essa referência, a quantidade
de PDFs das pastas expandidas, a presença do termo no arquivo selecionado e a
reconstrução idêntica dos três relatórios a partir dos JSONs. A comparação do
inventário final não detectou alteração de nomes, tamanhos ou timestamps de
modificação dos 62 arquivos; isso é uma verificação de metadados, não uma
garantia criptográfica ou um snapshot do acervo.

## 6. Artefatos e reprodução

Os artefatos locais desta execução estão em:

```text
resultados/validacao_docencia/1792399791315981000/
├── inventario.json
├── ambiente.json
├── auditoria_pdf.json
├── oraculo_conteudo.json
├── oraculo_nome.json
├── avisos_resumo.json
├── avisos_auditoria_pdf.log
├── avisos_etapa3.log
├── progresso_etapa3.json
├── verificacoes.json
├── etapa1/
├── etapa2/
└── etapa3/
```

JSONs e logs de auditoria são diferentes do esquema de execuções. Para converter
uma entrega, selecionar sua subpasta `etapaN`, sem misturar inventário e auditoria
com os registros dos algoritmos.

Com o acervo e o ambiente disponíveis, os comparativos podem ser repetidos por:

```sh
.venv/bin/python main.py --etapa 1 --raiz ../Docencia/Fontes --resultados resultados/docencia_nova/etapa1
.venv/bin/python main.py --etapa 2 --raiz ../Docencia/Fontes --alvo livro --alfa 100 --resultados resultados/docencia_nova/etapa2
.venv/bin/python main.py --etapa 3 --raiz ../Docencia/Fontes --alvo algoritmo --alfa 100 --resultados resultados/docencia_nova/etapa3
```

Os tempos dependem do ambiente e do cache. Os valores armazenados em bytes pelo
parser podem ser maiores ou menores que o tamanho físico de um PDF: incluem
releituras, mas o parser também pode deixar dados não necessários sem leitura.
