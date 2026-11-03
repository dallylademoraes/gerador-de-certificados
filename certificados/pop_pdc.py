"""
Modelo: Workshop POP (manhã) e Metodologia do PDC (tarde) — 08/04/2026

Formato do JSON (dados/pop_pdc.json):
    [
      {"nome": "Fulano de Tal", "manha": true, "tarde": false},
      {"nome": "Ciclana Silva", "manha": true, "tarde": true}
    ]
    (campos manha/tarde aceitam: true/false, "x"/"", 1/0)
"""

import os
from reportlab.pdfgen import canvas as rl_canvas

from .comum import (ASSETS, ASSINATURA, BRASAO, EQUIPE_COPLAN, PAGE_W, PAGE_H,
                    imagem, qr_email, registrar_fontes, truthy, wrap_mixed)

TITULO = "Workshop POP e Metodologia do PDC"
DADOS  = "pop_pdc.json"
FUNDO  = os.path.join(ASSETS, "fundo_pop_pdc.png")
CX     = PAGE_W / 2

# ── Configurações do evento ───────────────────────────────────────────────────
CONFIG = {
    "evento_manha":      "Workshop Procedimento Operacional Padrão (POP)",
    "evento_tarde":      "Metodologia do Plano de Desenvolvimento do Câmpus (PDC)",
    "carga_horaria":     "4 horas",
    "data_evento":       "08/04/2026",
    "promotor":          "Pró-Reitoria de Avaliação e Planejamento da Universidade Federal do Tocantins",
    "assinante_nome":    "Eduardo Andrea Lemus Erasmo",
    "assinante_cargo":   "Pró-Reitor de Avaliação e Planejamento",
    "email_contato":     "coplan@mail.uft.edu.br"
}

PALESTRANTES = [
    "vera nubia zandonadi gomes"
]

# Participante fictício usado em `python gerar.py pop_pdc --exemplo`
EXEMPLO = [{"nome": "Maria Aparecida dos Santos", "manha": True, "tarde": False}]


# ─────────────────────────────────────────────────────────────────────────────
# Desenho de um certificado
# ─────────────────────────────────────────────────────────────────────────────

def gerar_certificado(nome, evento, caminho_saida, qr_reader, texto_acao, texto_promovido, carga_horaria_atual):
    fn, fn_bold = registrar_fontes()
    c = rl_canvas.Canvas(caminho_saida, pagesize=(PAGE_W, PAGE_H))

    # Fundo
    c.drawImage(FUNDO, 0, 0, width=PAGE_W, height=PAGE_H)

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
    parts = [
        (texto_acao, False),
        (evento, True),
        (texto_promovido, False),
        (CONFIG["promotor"], False),
        (", com carga horária de ", False),
        (carga_horaria_atual, True),
        (".", False),
    ]
    wrap_mixed(c, parts, CX, 360, 610, 13, 19, fn, fn_bold)

    # Período do Evento
    c.setFont(fn_bold, 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(68, 248, "Período do Evento")
    c.setFont(fn, 11)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawString(68, 232, CONFIG["data_evento"])

    # Linha da assinatura
    sig_cx = CX - 30
    sig_w, sig_h = 120, 60
    sig_x = sig_cx - sig_w / 2
    line_y = 222
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.7)
    c.line(sig_x - 15, line_y, sig_x + sig_w + 35, line_y)
    c.drawImage(imagem(ASSINATURA), sig_x, line_y - 9,
                width=sig_w, height=sig_h, mask="auto")

    # Nome e cargo do assinante
    c.setFont(fn_bold, 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(sig_cx, 200, CONFIG["assinante_nome"])
    c.setFont(fn, 10)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(sig_cx, 187, CONFIG["assinante_cargo"])

    # QR Code (validação por e-mail)
    qr_size = 108
    qr_x = PAGE_W - 75 - qr_size
    qr_y = 160
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
        manha = truthy(p.get("manha", False))
        tarde = truthy(p.get("tarde", False))
        if not nome:
            continue

        nome_lower = nome.lower()

        # ── Palestrante: recebe somente o certificado de palestrante ──
        if nome_lower in PALESTRANTES:
            evento = "Gestão e Mapeamento de Processos Institucionais"
            carga = "8 horas"
            corpo = (f"Olá.\n\nGostaria de verificar a autenticidade do certificado de PALESTRANTE em nome de '{nome}', "
                     f"emitido para o evento:\n- {evento}\n\nCarga horária total: {carga}.\n\nAguardo confirmação.")
            qr = qr_email(CONFIG["email_contato"], "Validação de Certificado - Palestrante", corpo)
            yield nome, "PALESTRANTE", "PALESTRANTE", lambda arq, qr=qr, evento=evento, carga=carga: gerar_certificado(
                nome, evento, arq, qr, "Atuou como palestrante no evento ", ", promovido pela ", carga)
            continue

        # ── Organizador: certificado de organização (10h), além dos de participante ──
        if nome_lower in EQUIPE_COPLAN:
            evento = f"{CONFIG['evento_manha']} e {CONFIG['evento_tarde']}"
            corpo = (f"Olá.\n\nGostaria de verificar a autenticidade do certificado de ORGANIZADOR(A) em nome de '{nome}', "
                     f"emitido para os eventos:\n- {CONFIG['evento_manha']}\n- {CONFIG['evento_tarde']}\n\n"
                     f"Carga horária total: 10 horas.\n\nAguardo confirmação.")
            qr = qr_email(CONFIG["email_contato"], "Validação de Certificado - Organização", corpo)
            yield nome, "ORGANIZADOR - 10H", "ORG", lambda arq, qr=qr, evento=evento: gerar_certificado(
                nome, evento, arq, qr, "Participou da organização dos eventos ", ", promovidos pela ", "10 horas")

        # ── Participante (4h) por turno ──
        for ativo, evento, sufixo in [
            (manha, CONFIG["evento_manha"], "POP"),
            (tarde, CONFIG["evento_tarde"], "PDC"),
        ]:
            if not ativo:
                continue
            texto_acao = "Participou do " if sufixo == "POP" else "Participou da "
            corpo = (f"Olá.\n\nGostaria de verificar a autenticidade do certificado em nome de '{nome}', "
                     f"emitido para o evento '{evento}'.\n\nAguardo confirmação.")
            qr = qr_email(CONFIG["email_contato"], f"Validação de Certificado - Evento {sufixo}", corpo)
            rotulo = f"{sufixo} - OUVINTE 4H" if nome_lower in EQUIPE_COPLAN else sufixo
            yield nome, rotulo, sufixo, lambda arq, qr=qr, evento=evento, texto_acao=texto_acao: gerar_certificado(
                nome, evento, arq, qr, texto_acao, ", promovido pela ", CONFIG["carga_horaria"])
