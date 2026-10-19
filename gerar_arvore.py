"""Gere a árvore didática reproduzível em ./docencia/fontes/."""

import os


SEED = 2024
RAIZ = os.path.join("docencia", "fontes")


def gerar_arvore(raiz=RAIZ):
    """Crie 40 pastas abaixo da raiz e 64 arquivos com conteúdo fixo."""
    estado = SEED
    nomes = ("livro_algoritmos.txt", "plano_aula.md", "exemplo_busca.py",
             "diagrama.png")
    total_arquivos = 0
    for grupo in ("_planos_pedagogicos_2024", "_imagens_auxiliares",
                  "biblioteca", "laboratorio"):
        base = os.path.join(raiz, grupo)
        os.makedirs(base, exist_ok=True)
        for unidade in range(1, 4):
            pasta = os.path.join(base, "unidade_" + str(unidade))
            for nivel in ("", "aulas", os.path.join("aulas", "materiais")):
                os.makedirs(os.path.join(pasta, nivel), exist_ok=True)
            for indice, nome in enumerate(nomes):
                estado = (1664525 * estado + 1013904223) % (2 ** 32)
                destino = os.path.join(pasta, "aulas", "materiais", nome)
                if nome.endswith(".png"):
                    # PNG 1x1 válido; nenhum pacote externo é necessário.
                    dados = bytes.fromhex(
                        "89504e470d0a1a0a0000000d494844520000000100000001"
                        "0804000000b51c0c020000000b4944415478da6364f80f"
                        "00010501012718e3660000000049454e44ae426082")
                    with open(destino, "wb") as arquivo:
                        arquivo.write(dados)
                else:
                    conteudo = ("# Exemplo didático\nprint('Busca em pastas')\n"
                                if indice == 2 else "Material de apoio à docência.\n")
                    if indice < 2 and estado % 3 == 0:
                        conteudo += "Esta aula apresenta um algoritmo de busca.\n"
                    with open(destino, "w", encoding="utf-8") as arquivo:
                        arquivo.write(conteudo)
                total_arquivos += 1
        for nome in ("guia_docente.txt", "referencias.md", "notas.txt", "indice.md"):
            with open(os.path.join(base, nome), "w", encoding="utf-8") as arquivo:
                arquivo.write("Referências e organização do semestre.\n")
            total_arquivos += 1
    return 40, total_arquivos


if __name__ == "__main__":
    pastas, arquivos = gerar_arvore()
    print(f"Árvore criada em ./{RAIZ}/: {pastas} pastas abaixo da raiz, "
          f"{arquivos} arquivos (seed={SEED}).")
