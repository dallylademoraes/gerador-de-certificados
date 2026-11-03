"""
Gerador de Certificados — PROAP/COPLAN/UFT
==========================================
Uso:
    python gerar.py <modelo>              gera os certificados de todos em dados/<modelo>.json
    python gerar.py <modelo> --exemplo    gera só uma prévia (PDF + PNG) em exemplos/

Modelos disponíveis: veja MODELOS abaixo (ou rode `python gerar.py` sem argumentos).
"""

import os, sys

from certificados import oficina_riscos, pop_pdc
from certificados.comum import DADOS, EXEMPLOS, SAIDA, carregar_json, nome_arquivo

MODELOS = {
    "riscos":  oficina_riscos,
    "pop_pdc": pop_pdc,
}

# Evita erro ao imprimir ✓/✗ em terminais Windows que não usam UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def emitir(modelo, participantes, pasta):
    os.makedirs(pasta, exist_ok=True)
    gerados, erros, arquivos = 0, 0, []
    for nome, rotulo, sufixo, desenhar in modelo.certificados(participantes):
        arquivo = os.path.join(pasta, f"{nome_arquivo(nome)}_{sufixo}.pdf")
        try:
            desenhar(arquivo)
            print(f"  ✓  {nome}  [{rotulo}]")
            gerados += 1
            arquivos.append(arquivo)
        except Exception as e:
            print(f"  ✗  {nome}  [{rotulo}]  → {e}")
            erros += 1

    print(f"\n{'─'*50}")
    print(f"  Gerados : {gerados}")
    print(f"  Erros   : {erros}")
    print(f"  Saída   : {pasta}")
    return arquivos


def gerar_exemplo(chave, modelo):
    """Gera um certificado fictício e salva uma imagem PNG para visualização."""
    pdfs = emitir(modelo, modelo.EXEMPLO, EXEMPLOS)
    if not pdfs:
        return
    destino_pdf = os.path.join(EXEMPLOS, f"{chave}.pdf")
    os.replace(pdfs[0], destino_pdf)
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(f"\n  Prévia em PDF: {destino_pdf}")
        print("  (instale 'pymupdf' para gerar também a imagem PNG)")
        return
    destino_png = os.path.join(EXEMPLOS, f"{chave}.png")
    fitz.open(destino_pdf)[0].get_pixmap(dpi=120).save(destino_png)
    print(f"\n  Prévia: {destino_png}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    exemplo = "--exemplo" in sys.argv

    if len(args) != 1 or args[0] not in MODELOS:
        print(__doc__)
        print("Modelos:")
        for chave, modelo in MODELOS.items():
            print(f"  {chave:<10} {modelo.TITULO}   (dados/{modelo.DADOS})")
        sys.exit(1)

    chave = args[0]
    modelo = MODELOS[chave]

    if exemplo:
        gerar_exemplo(chave, modelo)
        return

    caminho = os.path.join(DADOS, modelo.DADOS)
    if not os.path.exists(caminho):
        print(f"[ERRO] Lista de participantes não encontrada: {caminho}")
        sys.exit(1)
    emitir(modelo, carregar_json(caminho), os.path.join(SAIDA, chave))


if __name__ == "__main__":
    main()
