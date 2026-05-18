"""
Reconstruye cursos_banco.json a partir del HTML generado por el Generador CeNET.
Uso: python parse_html_to_json.py catalogo.html
     python parse_html_to_json.py catalogo.html --out cursos_banco.json
"""
import sys, re, json
from bs4 import BeautifulSoup

def parse(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    cursos = []

    for cat_div in soup.select("[id^='cat_']"):
        # Nombre de categoría (el texto del header, sin "N cursos")
        hdr = cat_div.find("div", style=lambda s: s and "font-size:1.1rem" in (s or ""))
        if not hdr:
            continue
        span = hdr.find("span")
        if span:
            span.extract()
        cat_name = hdr.get_text(strip=True)

        for card in cat_div.select("[data-search]"):
            c = {"categoria": cat_name}

            # Imagen
            img = card.find("img")
            c["img"] = img["src"] if img else ""

            # Título
            tp = card.find("p", style=lambda s: s and "min-height:38px" in (s or ""))
            c["titulo"] = tp.get_text(strip=True) if tp else ""

            # Campos etiquetados dentro del <details>
            details = card.find("details")
            if not details:
                continue
            inner = details.find("div")
            if not inner:
                continue

            LABEL_MAP = {
                "familia profesional": "familia_prof",
                "nivel":               "nivel",
                "destinatarios":       "destinatarios",
                "conocimientos previos": "conocimientos",
            }
            ps = inner.find_all("p", recursive=False) or inner.find_all("p")
            i = 0
            sintesis_raw = ""
            while i < len(ps):
                p = ps[i]
                sty = p.get("style", "")
                txt = p.get_text(strip=True)
                if "text-transform:uppercase" in sty:
                    label = txt.lower().rstrip(":")
                    field = LABEL_MAP.get(label)
                    if field and i + 1 < len(ps):
                        c[field] = ps[i + 1].get_text(strip=True)
                        i += 2
                        continue
                elif "color:#374151" in sty or "color: rgb(55" in sty:
                    sintesis_raw = txt
                i += 1

            # Extraer curso_previo y síntesis limpia
            curso_previo = ""
            prereq_patterns = [
                r"Es nece[sc]?esario haber aprobado[^.]+\.",
                r"Es necesario tener aprobado[^.]+\.",
            ]
            sintesis = sintesis_raw
            for pat in prereq_patterns:
                m = re.search(pat, sintesis_raw, re.IGNORECASE)
                if m:
                    curso_previo = m.group(0)
                    sintesis = re.sub(
                        r"(Este curso tiene requisitos de inscripción\.?\s*|" + pat + r"\s*)",
                        "", sintesis_raw, flags=re.IGNORECASE
                    ).strip()
                    break
            c["curso_previo"] = curso_previo
            c["sintesis"]     = sintesis

            # Link de inscripción externo (no el mailto ni el forms por defecto)
            a = inner.find("a")
            href = (a.get("href", "") if a else "").strip()
            default_form = "forms.cloud.microsoft/r/rUh04Ht9vW"
            if href and href != "#" and default_form not in href:
                c["form_externo"] = href
            else:
                c["form_externo"] = ""

            cursos.append(c)

    return cursos


def main():
    args = sys.argv[1:]
    if not args:
        print("Uso: python parse_html_to_json.py catalogo.html [--out salida.json]")
        sys.exit(1)

    html_file = args[0]
    out_file  = "cursos_banco_reconstruido.json"
    if "--out" in args:
        out_file = args[args.index("--out") + 1]

    with open(html_file, encoding="utf-8") as f:
        html = f.read()

    cursos = parse(html)

    result = {
        "cursos":         cursos,
        "cohorte":        {},
        "titulo_oferta":  "Oferta Formativa CeNET 2026",
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(cursos)} cursos extraídos → {out_file}")


if __name__ == "__main__":
    main()
