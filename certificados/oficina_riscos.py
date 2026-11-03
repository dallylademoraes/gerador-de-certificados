"""
Modelo: Oficina de Gestão de Riscos (PROAP/COPLAN)

Mesmo estilo dos demais certificados (moldura azul, papel claro, cantos dourados),
desenhado em vetor — não depende de imagem de fundo.

Formato do JSON (dados/oficina_riscos.json):
    [
      {"nome": "Fulano de Tal", "setor": "a Pró-Reitoria de Graduação"},
      {"nome": "Ciclana Silva"}
    ]
    (o campo "setor" é opcional; se preenchido, aparece no texto como
     "representando <setor>" — por isso inclua o artigo: "a ...", "o ...")
"""

from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor

from .comum import (ASSINATURA, BRASAO, EQUIPE_COPLAN, PAGE_W, PAGE_H,
                    imagem, qr_email, registrar_fontes, wrap_mixed)

TITULO = "Oficina de Gestão de Riscos"
DADOS  = "oficina_riscos.json"
CX     = PAGE_W / 2

# ── Configurações do evento ───────────────────────────────────────────────────
CONFIG = {
    "evento":            "Oficina de Gestão de Riscos",
    "carga_horaria":     "4 horas",
    "carga_horaria_org": "8 horas",
    "data_evento":       "__/__/2026",
    "promotor":          "Pró-Reitoria de Avaliação e Planejamento da Universidade Federal do Tocantins",
    "assinante_nome":    "Eduardo Andrea Lemus Erasmo",
    "assinante_cargo":   "Pró-Reitor de Avaliação e Planejamento",
    "email_contato":     "coplan@mail.uft.edu.br",
}

# Participante fictício usado em `python gerar.py riscos --exemplo`
EXEMPLO = [{"nome": "Maria Aparecida dos Santos", "setor": "a Pró-Reitoria de Graduação"}]

# ── Paleta (a mesma do fundo dos outros certificados) ─────────────────────────
AZUL    = HexColor("#1F5B8A")
PAPEL   = HexColor("#F7F6F2")
DOURADO = HexColor("#A8843C")
FIO     = HexColor("#A3A69A")
# níveis de risco (tons suaves): baixo, médio, alto, extremo
RISCO   = [HexColor("#7FB89A"), HexColor("#E8C66E"), HexColor("#E39A5C"), HexColor("#D46A6A")]


def desenhar_moldura(c):
    """Moldura azul, papel claro, fio fino e cantos dourados."""
    c.setFillColor(AZUL)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    borda = 9
    c.setFillColor(PAPEL)
    c.rect(borda, borda, PAGE_W - 2 * borda, PAGE_H - 2 * borda, stroke=0, fill=1)

    m = 27
    c.setStrokeColor(FIO)
    c.setLineWidth(0.5)
    c.rect(m, m, PAGE_W - 2 * m, PAGE_H - 2 * m, stroke=1, fill=0)

    braco = 36
    c.setStrokeColor(DOURADO)
    c.setLineWidth(1.2)
    for x, y, dx, dy in [(m, m, 1, 1), (PAGE_W - m, m, -1, 1),
                         (m, PAGE_H - m, 1, -1), (PAGE_W - m, PAGE_H - m, -1, -1)]:
        c.line(x, y, x + dx * braco, y)
        c.line(x, y, x, y + dy * braco)


def desenhar_matriz_risco(c, x, y):
    """Pequena matriz de riscos 5x5 (probabilidade x impacto) como elemento decorativo."""
    cel, gap = 16, 3.5
    for prob in range(1, 6):
        for imp in range(1, 6):
            s = prob * imp
            nivel = 0 if s <= 4 else 1 if s <= 9 else 2 if s <= 16 else 3
            c.setFillColor(RISCO[nivel])
            c.roundRect(x + (imp - 1) * (cel + gap), y + (prob - 1) * (cel + gap),
                        cel, cel, 2.5, stroke=0, fill=1)


# ─────────────────────────────────────────────────────────────────────────────
# Desenho de um certificado
# ─────────────────────────────────────────────────────────────────────────────

def gerar_certificado(nome, partes_texto, caminho_saida, qr_reader):
    fn, fn_bold = registrar_fontes()
    c = rl_canvas.Canvas(caminho_saida, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(f"Certificado — {CONFIG['evento']} — {nome}")

    desenhar_moldura(c)
    desenhar_matriz_risco(c, 50, 48)

    # ── Canto Superior Esquerdo (Cabeçalho Institucional) ──
    c.setFillColorRGB(0.15, 0.15, 0.15)
    c.setFont(fn_bold, 12)
    c.drawString(50, PAGE_H - 60, "Universidade Federal do Tocantins")
    c.setFont(fn, 10)
    c.drawString(50, PAGE_H - 74, "Pró-Reitoria de Avaliação e Planejamento")
    c.setFont(fn_bold, 10)
    c.drawString(50, PAGE_H - 88, "PROAP")

    # ── Canto Superior Direito (Brasão UFT) ──
    brasao_size = 75
    c.drawImage(imagem(BRASAO), PAGE_W - brasao_size - 50, PAGE_H - brasao_size - 50,
                width=brasao_size, height=brasao_size,
                mask="auto", preserveAspectRatio=True)

    # CERTIFICADO
    c.setFont(fn_bold, 36)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(CX, 480, "CERTIFICADO")

    # Certificamos que
    c.setFont(fn, 14)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.drawCentredString(CX, 444, "Certificamos que")

    # Nome do participante
    fs_nome = 22
    while c.stringWidth(nome.upper(), fn_bold, fs_nome) > 600 and fs_nome > 13:
        fs_nome -= 1
    c.setFont(fn_bold, fs_nome)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(CX, 410, nome.upper())

    # Corpo do texto
    c.setFillColorRGB(0.15, 0.15, 0.15)
    wrap_mixed(c, partes_texto, CX, 365, 610, 13, 19, fn, fn_bold)

    # Período do Evento
    c.setFont(fn_bold, 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(68, 228, "Período do Evento")
    c.setFont(fn, 11)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawString(68, 212, CONFIG["data_evento"])

    # Linha da assinatura
    sig_cx = CX - 30
    sig_w, sig_h = 120, 60
    sig_x = sig_cx - sig_w / 2
    line_y = 202
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.7)
    c.line(sig_x - 15, line_y, sig_x + sig_w + 35, line_y)
    c.drawImage(imagem(ASSINATURA), sig_x, line_y - 9,
                width=sig_w, height=sig_h, mask="auto")

    # Nome e cargo do assinante
    c.setFont(fn_bold, 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(sig_cx, 180, CONFIG["assinante_nome"])
    c.setFont(fn, 10)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(sig_cx, 167, CONFIG["assinante_cargo"])

    # QR Code (validação por e-mail)
    qr_size = 108
    qr_x = PAGE_W - 75 - qr_size
    qr_y = 140
    c.setFont(fn, 7.5)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(qr_x + qr_size / 2, qr_y + qr_size + 9,
                        "Escaneie o QR Code para solicitar a validação por e-mail:")
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)

    c.save()


# ─────────────────────────────────────────────────────────────────────────────
# Regras de emissão
# ─────────────────────────────────────────────────────────────────────────────

def certificados(participantes):
    """
    Gera (nome, rótulo, sufixo do arquivo, função que desenha o PDF)
    para cada certificado a emitir.
    """
    for p in participantes:
        nome  = str(p.get("nome", "")).strip()
        setor = str(p.get("setor", "")).strip()
        if not nome:
            continue

        if nome.lower() in EQUIPE_COPLAN:
            papel, sufixo, carga = "ORGANIZADOR(A)", "ORG", CONFIG["carga_horaria_org"]
            partes = [
                ("Participou da organização da ", False),
                (CONFIG["evento"], True),
                (", promovida pela ", False),
                (CONFIG["promotor"], False),
                (", conduzindo junto às unidades da Reitoria o levantamento e a análise de seus riscos institucionais, com carga horária de ", False),
                (carga, True),
                (".", False),
            ]
        else:
            papel, sufixo, carga = "PARTICIPANTE", "PARTICIPANTE", CONFIG["carga_horaria"]
            unidade = [(", representando ", False), (setor, True)] if setor else []
            partes = [
                ("Participou da ", False),
                (CONFIG["evento"], True),
                (", promovida pela ", False),
                (CONFIG["promotor"], False),
                *unidade,
                (", contribuindo para a identificação e a análise dos riscos de sua unidade, com carga horária de ", False),
                (carga, True),
                (".", False),
            ]

        corpo = (f"Olá.\n\nGostaria de verificar a autenticidade do certificado de {papel} "
                 f"em nome de '{nome}', emitido para a {CONFIG['evento']} "
                 f"({CONFIG['data_evento']}).\n\nAguardo confirmação.")
        qr = qr_email(CONFIG["email_contato"], f"Validação de Certificado - {CONFIG['evento']}", corpo)
        yield nome, sufixo, sufixo, lambda arq, partes=partes, qr=qr: gerar_certificado(
            nome, partes, arq, qr)
