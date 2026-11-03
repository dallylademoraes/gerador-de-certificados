"""
Utilitários compartilhados por todos os modelos de certificado.
"""

import io, json, os, re, unicodedata, urllib.parse
from functools import lru_cache
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode

# ── Caminhos ─────────────────────────────────────────────────────────────────
RAIZ     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS   = os.path.join(RAIZ, "assets")
DADOS    = os.path.join(RAIZ, "dados")
SAIDA    = os.path.join(RAIZ, "saida")
EXEMPLOS = os.path.join(RAIZ, "exemplos")

ASSINATURA = os.path.join(ASSETS, "assinatura.png")
BRASAO     = os.path.join(ASSETS, "brasao_uft.png")

# ── Tamanho da página (A4 paisagem em pontos) ────────────────────────────────
PAGE_W, PAGE_H = 841.89, 595.28

# ── Equipe da COPLAN (recebe certificado de organização; nomes em minúsculo) ──
EQUIPE_COPLAN = [
    "adriana barbosa moura",
    "dallyla de moraes sousa",
    "doriete macedo santos",
    "fabiana pereira salgado carvalho",
    "herberth alves de souza",
    "idelma de melo rodrigues abreu",
    "joienita da silva carvalho santos",
    "jordana teixeira de melo",
    "vanderlan carneiro dias",
]


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


def carregar_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def imagem(caminho):
    """ImageReader em cache (evita reler o PNG a cada certificado)."""
    return ImageReader(caminho)


@lru_cache(maxsize=None)
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


def qr_email(email, assunto, corpo):
    """QR code com link mailto: para solicitar a validação do certificado."""
    link = (f"mailto:{email}?subject={urllib.parse.quote(assunto)}"
            f"&body={urllib.parse.quote(corpo)}")
    return gerar_qr(link)


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
