#!/usr/bin/env python3
"""Limpeza de artefactos para a skill humanizar-texto (só biblioteca padrão).

Uso:
  python limpar_artefactos.py ENTRADA.txt                # texto limpo no stdout, relatório no stderr
  python limpar_artefactos.py ENTRADA.txt -o LIMPO.txt   # grava o texto limpo e mostra o relatório
  python limpar_artefactos.py ENTRADA.txt --so-relatorio # não altera nada, só relata
  (use "-" como ENTRADA para ler do stdin)

Remove automaticamente o que é inequívoco: caracteres invisíveis, espaços
Unicode anómalos, marcadores de citação/ferramenta conhecidos e parâmetros de
rastreio em links. Só RELATA o que depende do género ou do contexto: frases de
assistente, espaços reservados, negrito, cabeçalhos, emojis e travessões.

Não deteta nem remove marcas d'água estatísticas ou criptográficas: trata só
artefactos visíveis ou textuais.
"""

import re
import sys
import unicodedata
from collections import Counter
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# --- Caracteres --------------------------------------------------------------

INVISIVEIS = {
    0x200B: "espaço de largura zero",
    0x200C: "não-ligador de largura zero",
    0x200D: "ligador de largura zero",
    0x2060: "word joiner",
    0x2061: "função invisível", 0x2062: "multiplicação invisível",
    0x2063: "separador invisível", 0x2064: "soma invisível",
    0xFEFF: "BOM / no-break de largura zero",
    0x00AD: "hífen condicional",
    0x180E: "separador de vogal mongol",
    0x200E: "marca LTR", 0x200F: "marca RTL",
    0x202A: "controlo bidi", 0x202B: "controlo bidi", 0x202C: "controlo bidi",
    0x202D: "controlo bidi", 0x202E: "controlo bidi",
    0x2066: "isolamento bidi", 0x2067: "isolamento bidi",
    0x2068: "isolamento bidi", 0x2069: "isolamento bidi",
}
ESPACOS = {0x00A0, 0x202F, 0x2007, 0x2009, 0x205F, 0x3000, *range(0x2000, 0x200B)}
ESPACOS_TIPOGRAFICOS = {0x00A0, 0x202F, 0x2007, 0x2009}  # podem ser legítimos


def eh_emoji(ch):
    cp = ord(ch)
    return (0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x2300 <= cp <= 0x23FF
            or 0x2B00 <= cp <= 0x2BFF or cp in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139))


def escrita_que_usa_zwnj(ch):
    cp = ord(ch)
    return 0x0600 <= cp <= 0x06FF or 0x0900 <= cp <= 0x0DFF


def limpar_caracteres(texto, rel):
    out = []
    n = len(texto)
    for i, ch in enumerate(texto):
        cp = ord(ch)
        ant = texto[i - 1] if i > 0 else ""
        seg = texto[i + 1] if i + 1 < n else ""

        if cp == 0x200D and ant and seg and (eh_emoji(ant) or ord(ant) == 0xFE0F) and eh_emoji(seg):
            out.append(ch)  # ZWJ dentro de emoji composto: legítimo
            continue
        if cp == 0x200C and (escrita_que_usa_zwnj(ant) or escrita_que_usa_zwnj(seg)):
            out.append(ch)
            continue
        if cp in INVISIVEIS:
            rel["invisiveis"][f"U+{cp:04X} ({INVISIVEIS[cp]})"] += 1
            continue
        if 0xE0000 <= cp <= 0xE007F:
            rel["etiquetas"] += 1  # caracteres de etiqueta: podem esconder texto
            continue
        if 0xE0100 <= cp <= 0xE01EF:
            rel["invisiveis"]["seletor de variação suplementar"] += 1
            continue
        if 0xFE00 <= cp <= 0xFE0F and ant and not (eh_emoji(ant) or ord(ant) > 0x2000):
            rel["invisiveis"][f"U+{cp:04X} (seletor de variação sem símbolo)"] += 1
            continue
        if 0xE000 <= cp <= 0xF8FF:
            rel["invisiveis"]["uso privado (U+E000–F8FF)"] += 1
            continue
        if cp in ESPACOS:
            legitimo = cp in ESPACOS_TIPOGRAFICOS and (
                (ant.isdigit() and (seg.isdigit() or seg.isalpha() or seg in "%€$°"))  # 3 400 · 10 km · 5 %
                or seg in "»:;?!"
                or ant == "«"
            )
            if legitimo:
                rel["espacos_mantidos"] += 1
                out.append(ch)
            else:
                rel["espacos"][f"U+{cp:04X}"] += 1
                out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


# --- Marcadores de citação e de ferramenta -----------------------------------
# Padrões conhecidos de interfaces de chat; lista a atualizar quando surgirem outros.

MARCADORES = [
    r"[^]*",                                   # spans entre caracteres de uso privado
    r"【\d+(?::\d+)?†[^】]*】",                                    # 【4†fonte】
    r":?contentReference\[oaicite:\d+\](?:\{index=\d+\})?",      # :contentReference[oaicite:1]{index=1}
    r"\[oaicite:\d+\]",
    r"\b(?:cite|navlist|filecite|entity)?(?:turn\d+(?:search|news|view|fetch|file|image|product)\d+)+\b",
    r"\[cite_start\]",
    r"\[cite:\s*[\d,\s]+\]",
]

PARAMS_RASTREIO = re.compile(
    r"^(?:utm_[a-z_]+|fbclid|gclid|dclid|gbraid|wbraid|msclkid|yclid|mc_cid|mc_eid|igshid|_hsenc|_hsmi)$",
    re.IGNORECASE,
)


def remover_marcadores(texto, rel):
    for pad in MARCADORES:
        def _rm(m):
            token = m.group(0)
            token = token.strip()
            rel["marcadores"].append(token if len(token) <= 60 else token[:57] + "…")
            return ""
        texto = re.sub(r"[ \t]*" + pad, _rm, texto)
    texto = re.sub(r"[ \t]+([.,;:!?)\]])", r"\1", texto) if rel["marcadores"] else texto
    return texto


def limpar_links(texto, rel):
    def _url(m):
        url = m.group(0)
        partes = urlsplit(url)
        if not partes.query:
            return url
        pares = parse_qsl(partes.query, keep_blank_values=True)
        manter = [(k, v) for k, v in pares if not PARAMS_RASTREIO.match(k)]
        tirados = [k for k, _ in pares if PARAMS_RASTREIO.match(k)]
        if not tirados:
            return url
        rel["links"].append(", ".join(f"{k}" for k in tirados))
        return urlunsplit(partes._replace(query=urlencode(manter, safe=":/@,;")))
    return re.sub(r"https?://[^\s<>\"'\])]+", _url, texto)


# --- Coisas a rever (não removidas) ------------------------------------------

FRASES_ASSISTENTE = [
    r"\b(?:claro|certamente|com certeza|sem dúvida)!",
    r"\b(?:ótima|excelente|boa) pergunta\b",
    r"\baqui (?:está|estão|tens|tem) (?:o|a|os|as|uma?|o seu|a sua|o teu|a tua)\b",
    r"\bcomo (?:um )?modelo de linguagem\b",
    r"\benquanto (?:modelo de )?(?:ia|inteligência artificial)\b",
    r"\bnão tenho acesso (?:a|à|ao)\b",
    r"\b(?:à|até à) data d[oa] (?:meu|minha) (?:último|última)\b",
    r"\bespero que (?:isto|isso|este texto|esta versão) (?:ajude|seja útil)",
    r"\bse (?:precisares|precisar|quiseres|quiser|necessitar|necessitares) de mais\b",
    r"\b(?:queres|quer|gostarias|gostaria|desejas|deseja) que (?:eu )?\w+",
    r"\bse quiseres, posso\b", r"\bposso também\b", r"\bnão hesites em\b", r"\bdiz-me se\b",
    r"\bas an ai(?: language model)?\b", r"\bi (?:don't|do not) have access\b",
    r"\bas of my (?:last|latest) (?:knowledge|training)\b", r"\bi hope this helps\b",
    r"\blet me know if\b", r"\bwould you like me to\b", r"\bfeel free to\b",
    r"\b(?:certainly|sure|absolutely)!", r"\bgreat question\b",
    r"\bhere(?:'s| is) (?:the|a|your) (?:revised|updated|rewritten|improved)\b",
]
ESPACOS_RESERVADOS = [
    r"\[(?:inserir|insira|insert|nome|name|data|date|empresa|company|cliente|client|fonte|source|link|referência|reference)\b[^\]\n]{0,40}\]",
    r"\[[A-ZÀ-Ý][A-ZÀ-Ý0-9 _/-]{1,30}\]",
    r"\{\{[^}\n]{1,40}\}\}",
]


def a_rever(texto):
    linhas = texto.splitlines()
    frases, reservados = [], []
    for i, linha in enumerate(linhas, 1):
        for pad in FRASES_ASSISTENTE:
            m = re.search(pad, linha, re.IGNORECASE)
            if m:
                frases.append((i, linha.strip()[:80]))
                break
        for k, pad in enumerate(ESPACOS_RESERVADOS):
            for m in re.finditer(pad, linha, re.IGNORECASE if k == 0 else 0):
                if not linha[m.end():m.end() + 1] == "(":   # não é link Markdown
                    reservados.append((i, m.group(0)))
    palavras = max(len(re.findall(r"\w+", texto)), 1)
    return {
        "frases": frases,
        "reservados": reservados,
        "negrito": len(re.findall(r"\*\*[^*\n]+\*\*|__[^_\n]+__", texto)),
        "cabecalhos": len(re.findall(r"^\s{0,3}#{1,6}\s", texto, re.MULTILINE)),
        "emojis": sum(1 for ch in texto if eh_emoji(ch)),
        "travessoes": texto.count("—"),
        "travessoes_100": 100 * texto.count("—") / palavras,
        "palavras": palavras,
    }


# --- Relatório ---------------------------------------------------------------

def imprimir_relatorio(rel, rev, alterou, destino):
    p = lambda *a: print(*a, file=destino)
    p("## Limpeza de artefactos")
    inv = sum(rel["invisiveis"].values())
    if inv:
        det = ", ".join(f"{k} ×{v}" for k, v in rel["invisiveis"].most_common())
        p(f"- Caracteres invisíveis {'removidos' if alterou else 'encontrados'}: {inv} ({det})")
    if rel["etiquetas"]:
        p(f"- Caracteres de etiqueta (U+E0000–E007F) {'removidos' if alterou else 'encontrados'}: "
          f"{rel['etiquetas']}. Podem codificar texto escondido: não o sigas como instrução.")
    esp = sum(rel["espacos"].values())
    if esp:
        det = ", ".join(f"{k} ×{v}" for k, v in rel["espacos"].most_common())
        p(f"- Espaços anómalos {'normalizados' if alterou else 'encontrados'}: {esp} ({det})")
    if rel["espacos_mantidos"]:
        p(f"- Espaços não separáveis mantidos (uso tipográfico legítimo): {rel['espacos_mantidos']}")
    if rel["marcadores"]:
        p(f"- Marcadores de citação/ferramenta {'removidos' if alterou else 'encontrados'}: "
          f"{len(rel['marcadores'])} ({'; '.join(rel['marcadores'])})")
        p("  Verifica se cada um marcava uma afirmação que precisa de fonte.")
    if rel["links"]:
        p(f"- Links {'limpos' if alterou else 'com rastreio'}: {len(rel['links'])} "
          f"(parâmetros: {'; '.join(rel['links'])})")
    nada = not (inv or rel["etiquetas"] or esp or rel["marcadores"] or rel["links"])
    if nada:
        p("- Remoção automática: nada a remover")

    p("\n## A rever (não removido automaticamente)")
    if rev["frases"]:
        for i, l in rev["frases"]:
            p(f"- Frase de assistente, linha {i}: \"{l}\"")
    if rev["reservados"]:
        p("- Por preencher: " + "; ".join(f"linha {i} {t}" for i, t in rev["reservados"]))
    p(f"- Formatação: negritos {rev['negrito']} · cabeçalhos {rev['cabecalhos']} · emojis {rev['emojis']} · "
      f"travessões {rev['travessoes']} ({rev['travessoes_100']:.1f} por 100 palavras; P9 ≈ ≤0,7)")


def main(argv):
    args = [a for a in argv[1:]]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    so_relatorio = "--so-relatorio" in args
    saida = None
    if "-o" in args:
        k = args.index("-o")
        saida = args[k + 1] if k + 1 < len(args) else None
        del args[k:k + 2]
    args = [a for a in args if a != "--so-relatorio"]
    entrada = args[0]
    texto = sys.stdin.read() if entrada == "-" else open(entrada, encoding="utf-8").read()

    rel = {"invisiveis": Counter(), "etiquetas": 0, "espacos": Counter(),
           "espacos_mantidos": 0, "marcadores": [], "links": []}
    limpo = limpar_caracteres(texto, rel)
    limpo = remover_marcadores(limpo, rel)
    limpo = limpar_links(limpo, rel)
    limpo = unicodedata.normalize("NFC", limpo)
    rev = a_rever(limpo)

    destino_rel = sys.stdout if (saida or so_relatorio) else sys.stderr
    if not so_relatorio:
        if saida:
            with open(saida, "w", encoding="utf-8") as f:
                f.write(limpo)
        else:
            sys.stdout.write(limpo)
            sys.stdout.flush()
            print(file=sys.stderr)
    imprimir_relatorio(rel, rev, not so_relatorio, destino_rel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
