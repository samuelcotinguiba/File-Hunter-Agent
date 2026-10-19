"""Gere PDFs pequenos e válidos para testes, sem biblioteca de geração."""


def criar_pdf(caminho, textos):
    """Crie uma página por texto, com fonte Helvetica e tabela xref correta."""
    filhos = " ".join(f"{4 + i * 2} 0 R" for i in range(len(textos)))
    objetos = [b"<< /Type /Catalog /Pages 2 0 R >>",
               f"<< /Type /Pages /Count {len(textos)} /Kids [{filhos}] >>".encode(),
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"]
    for i, texto in enumerate(textos):
        literal = texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        fluxo = f"BT /F1 12 Tf 72 720 Td ({literal}) Tj ET".encode("cp1252")
        objetos.extend([
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
             f"/Resources << /Font << /F1 3 0 R >> >> /Contents {5 + i * 2} 0 R >>").encode(),
            f"<< /Length {len(fluxo)} >>\nstream\n".encode() + fluxo + b"\nendstream",
        ])
    dados = bytearray(b"%PDF-1.4\n")
    posicoes = [0]
    for numero, objeto in enumerate(objetos, 1):
        posicoes.append(len(dados))
        dados.extend(f"{numero} 0 obj\n".encode() + objeto + b"\nendobj\n")
    inicio_xref = len(dados)
    dados.extend(f"xref\n0 {len(posicoes)}\n0000000000 65535 f \n".encode())
    for posicao in posicoes[1:]:
        dados.extend(f"{posicao:010d} 00000 n \n".encode())
    dados.extend((f"trailer\n<< /Size {len(posicoes)} /Root 1 0 R >>\n"
                  f"startxref\n{inicio_xref}\n%%EOF\n").encode())
    with open(caminho, "wb") as arquivo:
        arquivo.write(dados)
