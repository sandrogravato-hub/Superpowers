#!/usr/bin/env python3
"""Auditoria de apoio para a skill humanizar-texto (só biblioteca padrão).

Uso:
  python auditar_texto.py TEXTO.txt                  # mede padrões de um texto
  python auditar_texto.py ORIGINAL.txt REESCRITO.txt # mede os dois e compara factos
  (use "-" para ler um dos textos do stdin)

Isto NÃO é um detetor de IA. Mede, de forma heurística, padrões descritos nos
estudos citados no SKILL.md (ritmo de frases, gerúndios, nominalizações,
tríades, marcadores lexicais, fórmulas) e verifica se números, citações,
nomes próprios, negações e modais do original sobrevivem à reescrita.
Os resultados servem para orientar a leitura, não para a substituir.
"""

import re
import statistics
import sys
from collections import Counter

# --- Listas -----------------------------------------------------------------
# Regex com fronteira de palavra; formas flexionadas cobertas por \w*.

MARCADORES = {
    "pt": [
        r"tapeçaria\w*", r"testemunho", r"intrincad\w*", r"multifacetad\w*",
        r"crucia(?:l|is)", r"fundamenta(?:l|is)", r"essencia(?:l|is)", r"primordia(?:l|is)",
        r"vibrante\w*", r"palpáve(?:l|is)", r"camaradagem", r"fugaz(?:es)?",
        r"no (?:âmbito|domínio|panorama|cenário)", r"panorama", r"realç\w+", r"sublinh\w+",
        r"evidenci\w+", r"salient\w+", r"aprofund\w+", r"mergulh\w+", r"desvend\w+",
        r"foment\w+", r"potenci(?:ar|a|am|ando|ou|ado|ada)\b", r"alavanc\w+", r"capacit\w+",
        r"impulsion\w+", r"jornada\w*", r"naveg\w+", r"robust\w+", r"abrangente\w*",
        r"transformador\w*", r"inovador\w*", r"revolucion\w+", r"sinergia\w*",
        r"além disso", r"adicionalmente", r"ademais", r"outrossim",
        r"em suma", r"em conclusão", r"em última análise",
        r"é importante (?:notar|salientar|referir|sublinhar)", r"vale a pena (?:referir|notar|salientar)",
        r"num mundo (?:em que|onde|cada vez)", r"em constante evolução", r"quando se trata de",
        r"abr\w+ caminho", r"desempenh\w+ um papel", r"lado a lado", r"marco (?:crucial|importante|histórico)",
    ],
    "en": [
        r"tapestr\w*", r"testament", r"intricate\w*", r"multifaceted", r"crucial", r"pivotal",
        r"paramount", r"vibrant", r"palpable", r"camaraderie", r"solace", r"fleeting", r"amidst",
        r"unease", r"realm\w*", r"landscape\w*", r"showcas\w+", r"underscor\w+", r"delv\w+",
        r"dive into", r"foster\w*", r"harness\w*", r"elevat\w+", r"empower\w*", r"seamless\w*",
        r"robust", r"comprehensive", r"transformative", r"groundbreaking", r"grappl\w+",
        r"unravel\w*", r"ignit\w+", r"navigat\w+", r"journey\w*", r"resonat\w+",
        r"additionally", r"moreover", r"in conclusion", r"in summary",
        r"it'?s (?:important|crucial) to note", r"in a world (?:where|of)", r"when it comes to",
        r"pav\w+ the way", r"cautionary tale",
    ],
}

FORMULAS = {
    "pt": [
        (r"não só\b.{1,80}?\bmas também", "não só… mas também"),
        (r"não se trata (?:apenas |só )?de\b.{1,80}?\btrata-se de", "não se trata de X, trata-se de Y"),
        (r"não é (?:apenas|só|somente)\b.{1,60}?[—–:-]\s*é\b", "não é apenas X, é Y"),
        (r"^(?:espero que (?:este|esta) (?:email|e-mail|mensagem) (?:vos|te|o|a) encontre)", "cortesia de abertura"),
    ],
    "en": [
        (r"not only\b.{1,80}?\bbut also", "not only… but also"),
        (r"(?:it'?s|this is) not (?:just |only |merely )?(?:about )?.{1,60}?[—–,;:-]\s*it'?s", "it's not X, it's Y"),
        (r"^(?:i )?hope this (?:email|message) finds you", "pleasantry opener"),
        (r"^whether you'?re\b", "whether you're… opener"),
    ],
}

NEGACOES = {
    "pt": r"\b(?:não|nunca|nem|nenhum\w*|nada|jamais|sem)\b",
    "en": r"\b(?:not|no|never|none|nor|without|\w+n't)\b",
}
MODAIS = {
    "pt": r"\b(?:pode\w*|poder\w*|deve|devem|deverá|deverão|deveria\w*|devia\w*|talvez|provavelmente|possivelmente|cerca de|aproximadamente|sugere\w*|sugerem|parece\w*|indica\w*|mais de|menos de|até)\b",
    "en": r"\b(?:may|might|can|could|should|would|likely|probably|possibly|about|approximately|around|suggests?|appears?|seems?|more than|less than|up to)\b",
}
SUF_NOMINAL = {
    "pt": r"\b\w{3,}(?:ção|ções|mento|mentos|idade|idades|ência|ências|ância|âncias)\b",
    "en": r"\b\w{3,}(?:tion|tions|ment|ments|ness|ity|ities|ance|ence)\b",
}
GERUNDIO = {
    "pt": r",\s+\w+(?:ando|endo|indo)\b",
    "en": r",\s+(?!during\b|nothing\b|something\b|anything\b|everything\b|morning\b|evening\b)\w{3,}ing\b",
}
CONJ = {"pt": r"(?:e|ou)", "en": r"(?:and|or)"}
ABREV = r"(?:Dr|Dra|Sr|Sra|Prof|Profa|Eng|Mr|Mrs|Ms|St|etc|p\.\s?ex|e\.g|i\.e|vs|n\.º|nº)\."

PT_HINTS = {"que", "não", "de", "uma", "é", "os", "as", "para", "com", "em", "do", "da", "dos", "das"}
EN_HINTS = {"the", "and", "is", "of", "to", "that", "with", "for", "it", "this", "are", "was"}


# --- Utilitários ------------------------------------------------------------

def ler(caminho):
    if caminho == "-":
        return sys.stdin.read()
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def idioma(texto):
    palavras = re.findall(r"[a-zà-ÿ]+", texto.lower())
    pt = sum(p in PT_HINTS for p in palavras)
    en = sum(p in EN_HINTS for p in palavras)
    return "en" if en > pt else "pt"


def paragrafos(texto):
    blocos = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
    return blocos


def frases(texto):
    t = re.sub(ABREV, lambda m: m.group(0).replace(".", "§"), texto)
    partes = []
    for bloco in paragrafos(t):
        for linha in bloco.split("\n"):
            linha = linha.strip(" >-*•\t")
            if not linha:
                continue
            for s in re.split(r"(?<=[.!?…])[\"”»']?\s+(?=[\"“«'(]?[A-ZÀ-Ý0-9])", linha):
                s = s.replace("§", ".").strip()
                if s:
                    partes.append(s)
    return partes


def palavras(texto):
    return re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9'’\-]*", texto)


def letras(p):
    return sum(c.isalpha() for c in p)


def cv(valores):
    if len(valores) < 2:
        return 0.0
    media = statistics.mean(valores)
    return statistics.pstdev(valores) / media if media else 0.0


def maior_sequencia_parecida(comps, tolerancia=3):
    if not comps:
        return 0
    melhor = atual = 1
    for a, b in zip(comps, comps[1:]):
        atual = atual + 1 if abs(a - b) <= tolerancia else 1
        melhor = max(melhor, atual)
    return melhor


def contar(padrao, texto, flags=re.IGNORECASE):
    return len(re.findall(padrao, texto, flags))


def sem_citacoes(texto):
    """Apaga o interior das citações: o que está entre aspas não se reescreve."""
    return re.sub(r'["“«][^"”»\n]*["”»]', '""', texto)


# --- Métricas ---------------------------------------------------------------

def medir(texto, lang):
    fs = frases(texto)
    comps = [len(palavras(f)) for f in fs]
    ws = palavras(texto)
    n = max(len(ws), 1)
    pars = paragrafos(texto)
    comp_par = [len(palavras(p)) for p in pars]
    so_letras = [w for w in ws if letras(w) > 0]

    livre = sem_citacoes(texto)
    marc = Counter()
    for pad in MARCADORES[lang]:
        for m in re.finditer(r"\b" + pad + r"\b", livre, re.IGNORECASE):
            marc[m.group(0).lower()] += 1

    formulas = []
    for pad, nome in FORMULAS[lang]:
        alvo = livre if not pad.startswith("^") else "\n".join(l.strip() for l in livre.splitlines())
        k = len(re.findall(pad, alvo, re.IGNORECASE | re.MULTILINE | re.DOTALL))
        if k:
            formulas.append((nome, k))

    item = r"[\wÀ-ÿ-]+(?:\s[\wÀ-ÿ-]+){0,3}"
    triades = contar(rf"{item},\s{item},?\s{CONJ[lang]}\s[\wÀ-ÿ-]+", texto)

    aberturas = Counter(palavras(p)[0].lower() for p in pars if palavras(p))
    repetidas = {w: k for w, k in aberturas.items() if k >= 2 and len(pars) >= 3}

    return {
        "palavras": len(ws),
        "frases": len(fs),
        "paragrafos": len(pars),
        "frase_media": statistics.mean(comps) if comps else 0,
        "frase_min_max": (min(comps), max(comps)) if comps else (0, 0),
        "frase_cv": cv(comps),
        "frases_curtas": sum(c <= 8 for c in comps),
        "seq_parecida": maior_sequencia_parecida(comps),
        "comps": comps,
        "paragrafo_cv": cv(comp_par),
        "palavra_media": statistics.mean(letras(w) for w in so_letras) if so_letras else 0,
        "gerundios": contar(GERUNDIO[lang], texto),
        "nominal_100": 100 * contar(SUF_NOMINAL[lang], texto) / n,
        "triades": triades,
        "marcadores": marc,
        "formulas": formulas,
        "negrito_rotulo": contar(r"^\s*(?:[-*•]|\d+\.)\s+\*\*[^*\n]+?:?\*\*:?", texto, re.MULTILINE),
        "travessoes_100": 100 * texto.count("—") / n,
        "aberturas_repetidas": repetidas,
    }


def relatorio(nome, m):
    print(f"## {nome}")
    print(f"- {m['palavras']} palavras · {m['frases']} frases · {m['paragrafos']} parágrafos")
    mn, mx = m["frase_min_max"]
    print(f"- Frase: média {m['frase_media']:.1f} palavras (mín. {mn}, máx. {mx}); "
          f"variação (CV) {m['frase_cv']:.2f}; curtas (≤8): {m['frases_curtas']}")
    print(f"- Comprimentos: {m['comps']}")
    print(f"- Maior sequência de frases com comprimento parecido (±3): {m['seq_parecida']}  [P3: ≤3]")
    print(f"- Variação do tamanho dos parágrafos (CV): {m['paragrafo_cv']:.2f}")
    print(f"- Comprimento médio de palavra: {m['palavra_media']:.2f} letras")
    print(f"- Gerúndios/particípios depois de vírgula: {m['gerundios']}  [P1: ≤1 por parágrafo]")
    print(f"- Nominalizações (sufixos) por 100 palavras: {m['nominal_100']:.1f}")
    print(f"- Enumerações tipo 'A, B e C': {m['triades']}  [P5]")
    marc = ", ".join(f"{w} ({k})" for w, k in m["marcadores"].most_common()) or "nenhum"
    print(f"- Marcadores do glossário: {marc}  [P4]")
    form = ", ".join(f"{n} ({k})" for n, k in m["formulas"]) or "nenhuma"
    print(f"- Fórmulas: {form}")
    if m["negrito_rotulo"]:
        print(f"- Listas com rótulo a negrito: {m['negrito_rotulo']}  [R15]")
    print(f"- Travessões por 100 palavras: {m['travessoes_100']:.1f}")
    if m["aberturas_repetidas"]:
        ab = ", ".join(f"'{w}' ×{k}" for w, k in m["aberturas_repetidas"].items())
        print(f"- Parágrafos que abrem com a mesma palavra: {ab}  [R12]")
    print()


# --- Comparação de factos ---------------------------------------------------

def numeros(texto):
    return Counter(re.findall(r"\d+(?:[.,]\d+)*(?:\s?%|h\d*)?", texto))


def citacoes(texto):
    t = texto.replace("“", '"').replace("”", '"').replace("«", '"').replace("»", '"')
    return [c.strip() for c in re.findall(r'"([^"\n]{12,})"', t)]


def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("«", '"').replace("»", '"')
    return re.sub(r"\s+", " ", s).strip()


def nomes_proprios(texto):
    """Palavras com maiúscula que não estão só em início de frase."""
    meio, inicio = Counter(), Counter()
    for f in (seg for fr in frases(texto) for seg in re.split(r":\s+", fr)):
        toks = re.findall(r"[A-Za-zÀ-ÿ][\wÀ-ÿ'’\-]*", f)
        for i, t in enumerate(toks):
            if t[0].isupper() and len(t) > 1:
                (inicio if i == 0 else meio)[t] += 1
    return {t for t in meio} | {t for t in inicio if t in meio}


def comparar(orig, novo, lang):
    print("## Comparação de conteúdo (original → reescrito)")
    alertas = 0

    no, nn = numeros(orig), numeros(novo)
    faltam = sorted(set(no) - set(nn))
    novos = sorted(set(nn) - set(no))
    if faltam:
        alertas += 1
        print(f"- ATENÇÃO, números que desapareceram: {', '.join(faltam)}")
    if novos:
        alertas += 1
        print(f"- ATENÇÃO, números que não estavam no original: {', '.join(novos)}")
    if not faltam and not novos:
        print(f"- Números: todos os valores mantidos ({len(no)})")
    mudou = {k: (no[k], nn[k]) for k in set(no) & set(nn) if no[k] != nn[k]}
    if mudou:
        info = ", ".join(f"{k} ({a}→{b})" for k, (a, b) in sorted(mudou.items()))
        print(f"  (nº de ocorrências mudou, normal se for só repetição: {info})")

    novo_n = norm(novo)
    perdidas = [c for c in citacoes(orig) if norm(c) not in novo_n]
    if perdidas:
        alertas += 1
        for c in perdidas:
            print(f"- ATENÇÃO, citação alterada ou ausente: \"{c}\"")
    else:
        print(f"- Citações literais: todas presentes ({len(citacoes(orig))})")

    po, pn = nomes_proprios(orig), nomes_proprios(novo)
    tokens_novo = set(re.findall(r"[\wÀ-ÿ'’\-]+", novo))
    sumidos = sorted(p for p in po if p not in tokens_novo)
    aparecidos = sorted(p for p in pn - po if p not in set(re.findall(r"[\wÀ-ÿ'’\-]+", orig)))
    if sumidos:
        alertas += 1
        print(f"- ATENÇÃO, nomes próprios ausentes: {', '.join(sumidos)}")
    if aparecidos:
        alertas += 1
        print(f"- ATENÇÃO, nomes próprios novos: {', '.join(aparecidos)}")
    if not sumidos and not aparecidos:
        print("- Nomes próprios: sem perdas nem acréscimos")

    for rotulo, pad in (("negações", NEGACOES[lang]), ("modais/atenuadores", MODAIS[lang])):
        a, b = contar(pad, orig), contar(pad, novo)
        if a != b:
            alertas += 1
            print(f"- Verificar {rotulo}: {a} no original, {b} no reescrito "
                  f"(confirma que o sentido e o grau de certeza se mantêm)")
        else:
            print(f"- {rotulo.capitalize()}: {a} = {b}")

    print(f"\n{alertas} ponto(s) a verificar à mão." if alertas else "\nSem alertas automáticos. Lê na mesma.")


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    textos = [ler(c) for c in argv[1:]]
    lang = idioma(textos[0])
    print(f"Idioma detetado: {lang}\n")
    nomes = ["Texto"] if len(textos) == 1 else ["Original", "Reescrito"]
    for nome, t in zip(nomes, textos):
        relatorio(nome, medir(t, lang))
    if len(textos) == 2:
        comparar(textos[0], textos[1], lang)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
