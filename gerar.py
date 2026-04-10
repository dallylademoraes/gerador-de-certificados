"""
Gerador de Certificados — COPLAN/UFT
=====================================
Uso:
    python gerar.py

Estrutura esperada:
    gerador_certificados/
    ├── gerar.py              ← este arquivo
    ├── participantes.json    ← sua planilha exportada
    ├── fundo.png             ← plano de fundo do certificado
    ├── assinatura.png        ← assinatura (fundo transparente)
    ├── brasao_uft.png        ← brasão da UFT
    └── saida/                ← PDFs gerados aqui (criado automaticamente)

Formato do JSON:
    [
      {"nome": "Fulano de Tal", "manha": true, "tarde": false},
      {"nome": "Ciclana Silva", "manha": true, "tarde": true},
      ...
    ]
    (campos manha/tarde aceitam: true/false, "x"/"", 1/0)
"""

import json, os, io, re, unicodedata, sys
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import urllib.parse

# ── Caminhos ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
JSON_FILE  = os.path.join(BASE_DIR, "participantes.json")
FUNDO      = os.path.join(BASE_DIR, "fundo.png")
ASSINATURA = os.path.join(BASE_DIR, "assinatura.png")
BRASAO     = os.path.join(BASE_DIR, "brasao_uft.png")
SAIDA_DIR  = os.path.join(BASE_DIR, "saida")

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

# ── Listas Especiais (Nomes em minúsculo) ─────────────────────────────────────
PALESTRANTES = [
    "vera nubia zandonadi gomes"
]

ORGANIZADORES = [
    "adriana barbosa moura",
    "dallyla de moraes sousa",
    "doriete macedo santos",
    "fabiana pereira salgado carvalho",
    "herberth alves de souza",
    "idelma de melo rodrigues abreu",
    "joienita da silva carvalho santos",
    "jordana teixeira de melo",
    "vanderlan carneiro dias"
]

# ── Tamanho da página (A4 paisagem em pontos) ────────────────────────────────
PAGE_W, PAGE_H = 841.89, 595.28
CX = PAGE_W / 2

# ─────────────────────────────────────────────────────────────────────────────
# Utilitários
# ─────────────────────────────────────────────────────────────────────────────

def nome_arquivo(nome):
    """Remove acentos e caracteres especiais para usar no nome do arquivo."""
    nfkd = unicodedata.normalize("NFKD", nome)
    ascii_ = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^\w\s-]", "", ascii_).strip().replace(" ", "_")


def truthy(val):
    """Interpreta vários formatos de 'verdadeiro'."""
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("x", "1", "true", "sim", "s", "yes")


def registrar_fontes():
    """Registra fontes TrueType se disponíveis, senão usa Helvetica."""
    caminhos = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        # macOS
        "/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    try:
        reg = next((p for p in caminhos[::2] if os.path.exists(p)), None)
        bol = next((p for p in caminhos[1::2] if os.path.exists(p)), None)
        if reg and bol:
            pdfmetrics.registerFont(TTFont("Cert", reg))
            pdfmetrics.registerFont(TTFont("Cert-Bold", bol))
            return "Cert", "Cert-Bold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


def gerar_qr(texto):
    """Gera QR code e retorna como ImageReader do ReportLab."""
    qr = qrcode.QRCode(version=2, box_size=5, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf)


def wrap_mixed(c, parts, cx, y, max_w, fs, lh, fn, fn_bold):
    """
    Desenha texto misto (normal/negrito) com quebra de linha automática,
    centralizado horizontalmente.
    """
    tokens = []
    for txt, bold in parts:
        words = txt.split(" ")
        for i, w in enumerate(words):
            if w:
                tokens.append((w, bold))
            if i < len(words) - 1:
                tokens.append((" ", bold))

    lines, cur, cur_w = [], [], 0
    for word, bold in tokens:
        f = fn_bold if bold else fn
        tw = c.stringWidth(word, f, fs)
        if cur_w + tw <= max_w or not cur:
            cur.append((word, bold)); cur_w += tw
        else:
            while cur and cur[-1][0] == " ": cur.pop()
            lines.append(cur)
            cur = [] if word == " " else [(word, bold)]
            cur_w = 0 if word == " " else tw
    if cur:
        while cur and cur[-1][0] == " ": cur.pop()
        lines.append(cur)

    for line in lines:
        total = sum(c.stringWidth(w, fn_bold if b else fn, fs) for w, b in line)
        x = cx - total / 2
        for word, bold in line:
            f = fn_bold if bold else fn
            c.setFont(f, fs)
            c.drawString(x, y, word)
            x += c.stringWidth(word, f, fs)
        y -= lh
    return y


# ─────────────────────────────────────────────────────────────────────────────
# Geração de um certificado
# ─────────────────────────────────────────────────────────────────────────────

def gerar_certificado(nome, evento, caminho_saida, fn, fn_bold, qr_reader, sig_reader, brasao_reader, texto_acao, texto_promovido, carga_horaria_atual):
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

    # Fundo
    c.drawImage(FUNDO, 0, 0, width=PAGE_W, height=PAGE_H)

    # ── Canto Superior Esquerdo (Cabeçalho Institucional) ──
    c.setFillColorRGB(0.15, 0.15, 0.15)
    
    # 1. Universidade
    c.setFont(fn_bold, 12)
    c.drawString(50, PAGE_H - 60, "Universidade Federal do Tocantins")
    
    # 2. Pró-reitoria
    c.setFont(fn, 10)
    c.drawString(50, PAGE_H - 74, "Pró-Reitoria de Avaliação e Planejamento")
    
    # 3. PROAP
    c.setFont(fn_bold, 10)
    c.drawString(50, PAGE_H - 88, "PROAP")

    # ── Canto Superior Direito (Brasão UFT) ──
    brasao_size = 75 
    brasao_x = PAGE_W - brasao_size - 50 
    brasao_y = PAGE_H - brasao_size - 50 
    
    c.drawImage(brasao_reader, brasao_x, brasao_y, 
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
    
    # Montagem dinâmica do texto
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

    # Imagem da assinatura (DESCIDA EM -9 PONTOS)
    c.drawImage(sig_reader, sig_x, line_y - 9,
                width=sig_w, height=sig_h, mask="auto")

    # Nome e cargo do assinante
    c.setFont(fn_bold, 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(sig_cx, 200, CONFIG["assinante_nome"])
    c.setFont(fn, 10)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(sig_cx, 187, CONFIG["assinante_cargo"])

    # QR Code Dinâmico (E-mail)
    qr_size = 108
    qr_x = PAGE_W - 75 - qr_size
    qr_y = 160
    c.setFont(fn, 7.5)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawCentredString(qr_x + qr_size / 2, qr_y + qr_size + 9,
                        "Escaneie o QR Code para solicitar a validação por e-mail:")
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)

    c.save()
    with open(caminho_saida, "wb") as f:
        f.write(buf.getvalue())


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # Verifica arquivos obrigatórios
    arquivos_necessarios = [
        (JSON_FILE, "participantes.json"), 
        (FUNDO, "fundo.png"), 
        (ASSINATURA, "assinatura.png"),
        (BRASAO, "brasao_uft.png")
    ]
    
    for arq, label in arquivos_necessarios:
        if not os.path.exists(arq):
            print(f"[ERRO] Arquivo não encontrado: {arq}")
            print(f"       Coloque '{label}' na pasta do projeto.")
            sys.exit(1)

    os.makedirs(SAIDA_DIR, exist_ok=True)

    # Carrega dados
    with open(JSON_FILE, encoding="utf-8") as f:
        participantes = json.load(f)

    # Pré-carrega assets reutilizáveis
    fn, fn_bold   = registrar_fontes()
    sig_reader    = ImageReader(ASSINATURA)
    brasao_reader = ImageReader(BRASAO)

    gerados, erros = 0, 0

    for p in participantes:
        nome  = str(p.get("nome", "")).strip()
        manha = truthy(p.get("manha", False))
        tarde = truthy(p.get("tarde", False))

        if not nome:
            continue

        nome_lower = nome.lower()
        is_palestrante = nome_lower in PALESTRANTES
        is_organizador = nome_lower in ORGANIZADORES

        if is_palestrante:
            # ── LÓGICA EXCLUSIVA PARA PALESTRANTES ──
            evento_palestrante = "Gestão e Mapeamento de Processos Institucionais"
            sufixo = "PALESTRANTE"
            arquivo = os.path.join(SAIDA_DIR, f"{nome_arquivo(nome)}_{sufixo}.pdf")
            
            texto_acao = "Atuou como palestrante no evento "
            texto_promovido = ", promovido pela "
            carga_horaria_atual = "8 horas" 
            
            assunto = "Validação de Certificado - Palestrante"
            corpo = f"Olá.\n\nGostaria de verificar a autenticidade do certificado de PALESTRANTE em nome de '{nome}', emitido para o evento:\n- {evento_palestrante}\n\nCarga horária total: {carga_horaria_atual}.\n\nAguardo confirmação."
            
            assunto_encoded = urllib.parse.quote(assunto)
            corpo_encoded = urllib.parse.quote(corpo)
            link_mailto = f"mailto:{CONFIG['email_contato']}?subject={assunto_encoded}&body={corpo_encoded}"
            qr_reader_dinamico = gerar_qr(link_mailto)

            try:
                gerar_certificado(nome, evento_palestrante, arquivo, fn, fn_bold, qr_reader_dinamico, sig_reader, brasao_reader, texto_acao, texto_promovido, carga_horaria_atual)
                print(f"  ✓  {nome}  [PALESTRANTE]")
                gerados += 1
            except Exception as e:
                print(f"  ✗  {nome}  [PALESTRANTE]  → {e}")
                erros += 1
            
            # Palestrante não recebe os outros certificados normais
            continue 

        # ── SE FOR ORGANIZADOR, GERA PRIMEIRO O DE ORGANIZAÇÃO (10H) ──
        if is_organizador:
            evento_unificado = f"{CONFIG['evento_manha']} e {CONFIG['evento_tarde']}"
            sufixo = "ORG"
            arquivo = os.path.join(SAIDA_DIR, f"{nome_arquivo(nome)}_{sufixo}.pdf")
            
            texto_acao = "Participou da organização dos eventos "
            texto_promovido = ", promovidos pela "
            carga_horaria_atual = "10 horas"
            
            assunto = "Validação de Certificado - Organização"
            corpo = f"Olá.\n\nGostaria de verificar a autenticidade do certificado de ORGANIZADOR(A) em nome de '{nome}', emitido para os eventos:\n- {CONFIG['evento_manha']}\n- {CONFIG['evento_tarde']}\n\nCarga horária total: 10 horas.\n\nAguardo confirmação."
            
            assunto_encoded = urllib.parse.quote(assunto)
            corpo_encoded = urllib.parse.quote(corpo)
            link_mailto = f"mailto:{CONFIG['email_contato']}?subject={assunto_encoded}&body={corpo_encoded}"
            qr_reader_dinamico = gerar_qr(link_mailto)

            try:
                gerar_certificado(nome, evento_unificado, arquivo, fn, fn_bold, qr_reader_dinamico, sig_reader, brasao_reader, texto_acao, texto_promovido, carga_horaria_atual)
                print(f"  ✓  {nome}  [ORGANIZADOR - 10H]")
                gerados += 1
            except Exception as e:
                print(f"  ✗  {nome}  [ORGANIZADOR - 10H]  → {e}")
                erros += 1

        # ── AGORA GERA OS CERTIFICADOS DE PARTICIPANTE (4H) PARA TODOS (INCLUINDO ORGANIZADORES) ──
        for turno, ativo, evento, sufixo in [
            ("manhã", manha, CONFIG["evento_manha"], "POP"),
            ("tarde", tarde, CONFIG["evento_tarde"], "PDC"),
        ]:
            if not ativo:
                continue
            
            arquivo = os.path.join(SAIDA_DIR, f"{nome_arquivo(nome)}_{sufixo}.pdf")
            
            texto_acao = "Participou do " if sufixo == "POP" else "Participou da "
            texto_promovido = ", promovido pela "
            carga_horaria_atual = CONFIG["carga_horaria"] # Puxa as 4 horas
            
            assunto = f"Validação de Certificado - Evento {sufixo}"
            corpo = f"Olá.\n\nGostaria de verificar a autenticidade do certificado em nome de '{nome}', emitido para o evento '{evento}'.\n\nAguardo confirmação."
            
            assunto_encoded = urllib.parse.quote(assunto)
            corpo_encoded = urllib.parse.quote(corpo)
            link_mailto = f"mailto:{CONFIG['email_contato']}?subject={assunto_encoded}&body={corpo_encoded}"
            qr_reader_dinamico = gerar_qr(link_mailto)

            try:
                gerar_certificado(nome, evento, arquivo, fn, fn_bold, qr_reader_dinamico, sig_reader, brasao_reader, texto_acao, texto_promovido, carga_horaria_atual)
                # Se for organizador recebendo o de participante, avisa no print pra você saber
                if is_organizador:
                    print(f"  ✓  {nome}  [{sufixo} - OUVINTE 4H]")
                else:
                    print(f"  ✓  {nome}  [{sufixo}]")
                gerados += 1
            except Exception as e:
                print(f"  ✗  {nome}  [{sufixo}]  → {e}")
                erros += 1

    print(f"\n{'─'*50}")
    print(f"  Gerados : {gerados}")
    print(f"  Erros   : {erros}")
    print(f"  Saída   : {SAIDA_DIR}")


if __name__ == "__main__":
    main()