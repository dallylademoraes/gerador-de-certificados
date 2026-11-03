# Gerador de Certificados — PROAP/COPLAN/UFT

## Estrutura

```
gerador-de-certificados/
├── gerar.py                  ← comando único para gerar certificados
├── certificados/             ← código dos modelos
│   ├── comum.py              ← funções compartilhadas + equipe COPLAN
│   ├── oficina_riscos.py     ← modelo: Oficina de Gestão de Riscos
│   └── pop_pdc.py            ← modelo: Workshop POP / Metodologia PDC
├── dados/                    ← listas de participantes (uma por evento)
│   ├── oficina_riscos.json
│   └── pop_pdc.json
├── assets/                   ← imagens (assinatura, brasão, fundos)
├── exemplos/                 ← prévias de cada modelo (PNG e PDF)
└── saida/                    ← PDFs gerados (um subdiretório por evento)
```

## Instalação (primeira vez)

```bash
pip install -r requirements.txt
```

## Como usar

```bash
python gerar.py riscos --exemplo   # só uma prévia → exemplos/riscos.png
python gerar.py riscos             # todos de dados/oficina_riscos.json → saida/riscos/
python gerar.py pop_pdc            # todos de dados/pop_pdc.json → saida/pop_pdc/
```

Rodar `python gerar.py` sem argumentos lista os modelos disponíveis.

## Formato das listas

**Oficina de Riscos** (`dados/oficina_riscos.json`):

```json
[
  {"nome": "Fulano de Tal", "setor": "a Pró-Reitoria de Graduação"},
  {"nome": "Ciclana Silva"}
]
```

`setor` é opcional. Quando preenchido, aparece como "representando **a Pró-Reitoria de Graduação**",
por isso inclua o artigo (a/o).

**POP / PDC** (`dados/pop_pdc.json`):

```json
[
  {"nome": "Fulano de Tal", "manha": true, "tarde": false},
  {"nome": "Ciclana Silva", "manha": true, "tarde": true}
]
```

`manha`/`tarde` aceitam `true`/`false`, `"x"`/`""`, `1`/`0`. Manhã gera o certificado **POP** e tarde gera o **PDC**.

## Regras especiais

- Quem está em `EQUIPE_COPLAN` (em `certificados/comum.py`) recebe o certificado de **organização**.
- No POP/PDC, quem está em `PALESTRANTES` (em `certificados/pop_pdc.py`) recebe só o certificado de palestrante.

## Personalizando um evento

Cada modelo tem um bloco `CONFIG` no topo do arquivo, com o nome do evento, a data, a carga horária,
quem assina e o e-mail de validação.

## Criando um modelo novo

1. Copie um dos arquivos de `certificados/` (por exemplo `oficina_riscos.py`) e ajuste `TITULO`, `DADOS`, `CONFIG`, `EXEMPLO` e o desenho.
2. Registre o modelo em `MODELOS`, no `gerar.py`.
3. Crie a lista em `dados/`.
