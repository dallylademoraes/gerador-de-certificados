# Gerador de Certificados — COPLAN/UFT

## Estrutura da pasta

```
gerador_certificados/
├── gerar.py              ← script principal
├── participantes.json    ← lista de participantes
├── fundo.jpg             ← plano de fundo do certificado
├── assinatura.png        ← assinatura (PNG com fundo transparente)
├── requirements.txt      ← dependências
└── saida/               ← PDFs gerados aqui (criado automaticamente)
```

## Instalação (primeira vez)

```bash
pip install -r requirements.txt
```

## Como usar

1. Coloque `fundo.jpg` e `assinatura.png` na pasta
2. Edite `participantes.json` com os participantes
3. Execute:

```bash
python gerar.py
```

Os PDFs aparecem na pasta `saida/`.

---

## Formato do JSON

```json
[
  {"nome": "Fulano de Tal",  "manha": true,  "tarde": false},
  {"nome": "Ciclana Silva",  "manha": true,  "tarde": true},
  {"nome": "Beltrano Costa", "manha": false, "tarde": true}
]
```

| Campo   | Aceita                              |
|---------|-------------------------------------|
| `manha` | `true`, `false`, `"x"`, `""`, `1`, `0` |
| `tarde` | `true`, `false`, `"x"`, `""`, `1`, `0` |

- `manha: true` → gera certificado **POP** (manhã)
- `tarde: true` → gera certificado **PDC** (tarde)
- Ambos `true` → gera **dois** certificados para a pessoa

---

## Personalizando o evento

Edite o bloco `CONFIG` no início do `gerar.py`:

```python
CONFIG = {
    "evento_manha":   "Workshop Procedimento Operacional Padrão (POP)",
    "evento_tarde":   "Metodologia do Plano de Desenvolvimento do Câmpus (PDC)",
    "carga_horaria":  "4 horas",
    "data_evento":    "08/03/2026",
    "promotor":       "Pró-Reitoria de Avaliação e Planejamento ...",
    "assinante_nome": "Eduardo Andrea Lemus Erasmo",
    "assinante_cargo":"Pró-Reitor de Avaliação e Planejamento",
    "qr_texto":       "Texto que vai no QR code...",
}
```
