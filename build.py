#!/usr/bin/env python3
"""Genera las páginas legales de bpurevel.com desde el borrador de Obsidian.

La fuente es UNA sola: `terminos-privacidad-y-centro-de-ayuda.md` del vault.
Este script no se edita para cambiar un texto: se cambia el .md y se vuelve a
correr.

Qué se publica:
  - Documento 1 (Términos) sin el Anexo A del Marketplace.
  - Documento 2 (Privacidad) sin P18, el aviso corto que va en la pantalla de
    registro de la app.
  - Documento 3 (Centro de ayuda).
  - Documento 4 (Eliminar cuenta).

Qué NO se publica: los callouts de Obsidian (`> [!question]`, `> [!info]`…),
que son notas de trabajo. La única excepción son los "Resumen en lenguaje
sencillo", que sí son para el público.

Uso:
    python3 -m venv .venv && .venv/bin/pip install markdown
    .venv/bin/python build.py [ruta-al-md]
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

SOURCE = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else Path.home()
    / "obsidian_boveda/baul_personal/purevel/terminos-privacidad-y-centro-de-ayuda.md"
)
OUT = Path(__file__).resolve().parent

# (carpeta, inicio, fin, rótulo del menú, descripción para buscadores)
PAGES = [
    (
        "terminos",
        "# DOCUMENTO 1",
        "## Anexo A",
        "Términos",
        "Términos y Condiciones de Uso de Purevel.",
    ),
    (
        "privacidad",
        "# DOCUMENTO 2",
        "# DOCUMENTO 3",
        "Privacidad",
        "Política de Tratamiento de Datos Personales y Privacidad de Purevel.",
    ),
    (
        "ayuda",
        "# DOCUMENTO 3",
        "# DOCUMENTO 4",
        "Ayuda",
        "Centro de ayuda de Purevel.",
    ),
    (
        "eliminar-cuenta",
        "# DOCUMENTO 4",
        "## Checklist de publicación",
        "Eliminar cuenta",
        "Cómo eliminar tu cuenta de Purevel y qué pasa con tus datos.",
    ),
]

SKIPPED_SECTIONS = ("## P18.",)
PUBLIC_CALLOUT = "Resumen en lenguaje sencillo"
CALLOUT = re.compile(r"^> \[!(\w+)\][+-]?\s*(.*)$")
WIKILINK_TO_HEADING = re.compile(r"\[\[#([^\]]+)\]\]")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")


def extract(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i : text.index(end, i)]


def drop_sections(md: str) -> str:
    out, skipping = [], False
    for line in md.split("\n"):
        if line.startswith("## "):
            skipping = line.startswith(SKIPPED_SECTIONS)
        elif line.startswith("# "):
            skipping = False
        if not skipping:
            out.append(line)
    return "\n".join(out)


def process_callouts(md: str) -> str:
    """Quita las notas internas y convierte los resúmenes en un recuadro."""
    lines, out, i = md.split("\n"), [], 0
    while i < len(lines):
        match = CALLOUT.match(lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        title = match.group(2).strip()
        body = []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            body.append(lines[i][2:] if lines[i].startswith("> ") else lines[i][1:])
            i += 1
        if title.startswith(PUBLIC_CALLOUT):
            inner = markdown.markdown("\n".join(body), extensions=["tables"])
            out += [
                "",
                '<aside class="summary"><p class="summary-title">'
                f"{html.escape(title)}</p>{inner}</aside>",
                "",
            ]
    return "\n".join(out)


def clean(md: str) -> tuple[str, str]:
    """Devuelve (título, markdown listo para convertir)."""
    first, rest = md.split("\n", 1)
    title = first.split("—", 1)[1].strip()
    rest = drop_sections(rest)
    rest = process_callouts(rest)
    rest = WIKILINK_TO_HEADING.sub(
        lambda m: f"[{m.group(1)}](#{slugify_unicode(m.group(1), '-')})", rest
    )
    rest = WIKILINK.sub(lambda m: m.group(2) or m.group(1), rest)
    # Los `---` separan documentos en el vault; en la web sobran.
    rest = re.sub(r"(?m)^---\s*$", "", rest)
    return title, rest.strip() + "\n"


LINKABLE_PAGES = "|".join(slug for slug, *_ in PAGES)


def link_text(body: str) -> str:
    body = re.sub(
        r"(?<![\w/.\"-])bpurevel\.com/(" + LINKABLE_PAGES + r")\b",
        r'<a href="../\1/">bpurevel.com/\1</a>',
        body,
    )
    body = re.sub(
        r"(?<![\w.:/\"-])((?:soporte|hola)@bpurevel\.com)",
        r'<a href="mailto:\1">\1</a>',
        body,
    )
    return re.sub(r"<table>", '<div class="table-wrap"><table>', body).replace(
        "</table>", "</table></div>"
    )


def nav(current: str | None, prefix: str) -> str:
    items = []
    for slug, _, _, label, _ in PAGES:
        attrs = ' aria-current="page"' if slug == current else ""
        items.append(f'<a href="{prefix}{slug}/"{attrs}>{label}</a>')
    return "\n        ".join(items)


def page(title: str, description: str, body: str, current: str | None, prefix: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · Purevel</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="icon" href="{prefix}favicon.png">
  <link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="{prefix}">purevel</a>
      <nav aria-label="Documentos">
        {nav(current, prefix)}
      </nav>
    </div>
  </header>
  <main class="wrap doc">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      Purevel · <a href="mailto:soporte@bpurevel.com">soporte@bpurevel.com</a>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    md = markdown.Markdown(
        extensions=["tables", "toc", "sane_lists"],
        extension_configs={"toc": {"slugify": slugify_unicode}},
    )
    for slug, start, end, _, description in PAGES:
        title, body_md = clean(extract(text, start, end))
        md.reset()
        body = f"<h1>{html.escape(title)}</h1>\n" + link_text(md.convert(body_md))
        target = OUT / slug / "index.html"
        target.parent.mkdir(exist_ok=True)
        target.write_text(page(title, description, body, slug, "../"), encoding="utf-8")
        print(f"  {slug}/index.html")

    cards = "\n".join(
        f'      <li><a href="{slug}/"><strong>{label}</strong><span>{html.escape(desc)}</span></a></li>'
        for slug, _, _, label, desc in PAGES
    )
    index = f"""<h1>Documentos de Purevel</h1>
    <p>Las reglas de uso, cómo tratamos tus datos, la ayuda y cómo eliminar tu cuenta.</p>
    <ul class="cards">
{cards}
    </ul>"""
    (OUT / "index.html").write_text(
        page("Documentos", "Términos, privacidad y ayuda de Purevel.", index, None, ""),
        encoding="utf-8",
    )
    print("  index.html")

    # GitHub Pages sirve 404.html en cualquier ruta que no exista, a cualquier
    # profundidad: las rutas tienen que ser absolutas o el CSS no carga.
    not_found = """<h1>No encontramos esta página</h1>
    <p>Puede que el enlace esté mal escrito o que la página ya no exista.</p>
    <p><a href="/">Ver todos los documentos</a></p>"""
    (OUT / "404.html").write_text(
        page("Página no encontrada", "Página no encontrada.", not_found, None, "/"),
        encoding="utf-8",
    )
    print("  404.html")


if __name__ == "__main__":
    main()
