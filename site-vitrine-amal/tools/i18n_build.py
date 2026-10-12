#!/usr/bin/env python3
"""Chaîne de traduction du site vitrine AMAL (français → anglais / wolof).

Principe
--------
Le français reste la langue de référence : il vit directement dans ``index.html``.
Ce script extrait, **dans un ordre déterministe**, tous les textes visibles
(nœuds de texte + attributs ``alt``/``placeholder``/``aria-label`` + balises
``title``/``meta``) et les apparie avec les traductions saisies ligne par ligne
dans ``tools/i18n/translations-en.txt`` et ``translations-wo.txt``.

Il produit ensuite ``assets/js/i18n-data.js`` : un dictionnaire
« texte français → traduction » consommé par ``assets/js/i18n.js`` au chargement
de la page. Ainsi, aucune clé n'est écrite à la main et une traduction ne peut
jamais se retrouver associée au mauvais texte.

Utilisation
-----------
    python3 tools/i18n_build.py            # (re)génère i18n-data.js + la référence
    python3 tools/i18n_build.py --check    # vérifie sans écrire (code retour 1 si écart)
    python3 tools/i18n_build.py --dump     # affiche la liste française numérotée
    python3 tools/i18n_build.py --accept   # après un changement de index.html (voir ci-dessous)

Fichiers de traduction
----------------------
Une ligne = une traduction, dans le même ordre que la liste française.
   * une ligne vide  → texte laissé en français (noms propres, chiffres, URL…)
   * ``-``           → identique au français (à conserver tel quel)

Si un texte est ajouté ou déplacé dans ``index.html``, la liste française change
d'un cran : le script s'arrête alors avec un message indiquant les index
concernés. Il faut réaligner ``translations-en.txt`` / ``translations-wo.txt``,
puis relancer avec ``--accept`` pour mettre à jour l'instantané
``tools/i18n/fr-master.txt``.
"""
from __future__ import annotations

import html as _html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
TRAD_DIR = ROOT / "tools" / "i18n"
OUT_JS = ROOT / "assets" / "js" / "i18n-data.js"
OUT_DOC = ROOT / "tools" / "i18n" / "reference.md"
BASELINE = TRAD_DIR / "fr-master.txt"

LANGS = {
    "en": TRAD_DIR / "translations-en.txt",
    "wo": TRAD_DIR / "translations-wo.txt",
}

SKIP_TAGS = {"script", "style", "svg"}
ATTRS = ("alt", "placeholder", "aria-label", "title")
META_KEYS = ("description", "og:title", "og:description", "og:image:alt", "keywords")

TAG_RE = re.compile(r"<(/?)([a-zA-Z0-9]+)([^>]*)>")
ATTR_RE = re.compile(r'([a-zA-Z:-]+)\s*=\s*"([^"]*)"')


class Node:
    """Élément minimal reconstruit à partir du HTML (sans dépendance externe)."""

    def __init__(self, tag: str, attrs: dict[str, str]) -> None:
        self.tag = tag
        self.attrs = attrs


def _clean(value: str) -> str:
    value = _html.unescape(value).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", value).strip()


def extract_master_list(html: str) -> tuple[list[str], list[str]]:
    """Renvoie (liste française ordonnée, texte des balises <title>/<meta>)."""
    head, _, body = html.partition("</head>")
    # Les commentaires de structure (<!-- ... -->) ne sont jamais traduits
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    texts: list[str] = []
    seen: set[str] = set()

    def push(value: str) -> None:
        value = _clean(value)
        if len(value) < 2 or value in seen:
            return
        seen.add(value)
        texts.append(value)

    # --- dans <body> : nœuds de texte puis attributs (ordre du document) ---
    # Deux raisons de ne rien extraire : les balises techniques (script/style/svg)
    # et les blocs explicitement marqués data-no-i18n (sélecteur de langue…).
    skip_depth = 0
    skip_name: str | None = None
    skip_nest = 0
    pos = 0
    text_buf: list[str] = []

    def flush() -> None:
        if skip_depth == 0 and skip_name is None and text_buf:
            push("".join(text_buf))
        text_buf.clear()

    for match in TAG_RE.finditer(body):
        chunk = body[pos:match.start()]
        pos = match.end()
        if chunk:
            text_buf.append(chunk)
        closing, tag, raw_attrs = match.group(1), match.group(2).lower(), match.group(3)
        if tag in SKIP_TAGS:
            flush()
            skip_depth += 1 if not closing else -1
            skip_depth = max(skip_depth, 0)
            continue
        if skip_name is not None:
            # On est dans un bloc data-no-i18n : on ne retient rien,
            # on compte seulement les balises du même nom pour trouver la sortie.
            flush()
            if tag == skip_name:
                skip_nest += -1 if closing else 1
                if skip_nest <= 0:
                    skip_name = None
            continue
        if not closing and "data-no-i18n" in raw_attrs:
            flush()
            skip_name, skip_nest = tag, 1
            continue
        # Toute balise clôt le fragment courant : on obtient exactement les
        # mêmes nœuds de texte que ceux visités par le navigateur.
        flush()
    flush()

    skip_name, skip_nest = None, 0
    for match in TAG_RE.finditer(body):
        closing, tag = match.group(1), match.group(2).lower()
        if tag in SKIP_TAGS:
            continue
        if skip_name is not None:
            if tag == skip_name:
                skip_nest += -1 if closing else 1
                if skip_nest <= 0:
                    skip_name = None
            continue
        if not closing and "data-no-i18n" in match.group(3):
            skip_name, skip_nest = tag, 1
            continue
        if closing:
            continue
        attrs = {k.lower(): v for k, v in ATTR_RE.findall(match.group(3))}
        for attr in ATTRS:
            if attrs.get(attr):
                push(attrs[attr])

    # --- <head> : titre, description et métadonnées de partage ---
    title = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
    metas: list[str] = []
    if title:
        metas.append(_clean(title.group(1)))
    for tag_raw in re.findall(r"<meta[^>]*>", head, re.I):
        attrs = {k.lower(): v for k, v in ATTR_RE.findall(tag_raw)}
        key = attrs.get("name") or attrs.get("property")
        if key in META_KEYS and attrs.get("content"):
            metas.append(_clean(attrs["content"]))
    return texts, metas


# Textes créés à la volée par assets/js/main.js (message de confirmation du
# formulaire) : ils ne sont pas dans index.html mais doivent être traduits.
RUNTIME_STRINGS = [
    "Nous ouvrons WhatsApp avec le récapitulatif de votre demande",
    "(cliquez ici si rien ne s'ouvre)",
    "Vous préférez l'e-mail ?",
    "Envoyez votre demande par e-mail",
]

INDEXED_RE = re.compile(r"^\s*(\d+)\s*\| ?(.*)$")


def load_lines(path: Path, expected: int) -> tuple[list[str], list[int]]:
    """Renvoie (traductions alignées sur l'index, index manquants).

    Un index explicite en début de ligne (``12|texte``) est recommandé : il rend
    impossible tout décalage. Sans index, la ligne suit simplement l'ordre de la
    liste française.
    """
    values = [""] * expected
    if not path.exists():
        return values, list(range(expected))

    missing: list[int] = []
    cursor = 0
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.rstrip()
        match = INDEXED_RE.match(line)
        if match:
            idx, value = int(match.group(1)), match.group(2).strip()
        elif line.strip():
            idx, value = cursor, line.strip()
        else:
            cursor += 1
            continue
        if 0 <= idx < expected:
            values[idx] = value
        cursor = idx + 1
    missing = [i for i, v in enumerate(values) if not v]
    return values, missing


def check_baseline(entries: list[str], accept: bool) -> bool:
    """Empêche un décalage silencieux des traductions.

    Les fichiers ``translations-xx.txt`` sont alignés **par index** sur la liste
    française. Si une modification de ``index.html`` change cette liste (texte
    ajouté, supprimé ou déplacé), toutes les traductions situées après glissent
    d'un cran. On compare donc la liste courante à l'instantané
    ``tools/i18n/fr-master.txt`` et on s'arrête net en cas d'écart.
    """
    printed = "\n".join(f"{i}|{t}" for i, t in enumerate(entries))
    if not BASELINE.exists():
        BASELINE.write_text(printed + "\n", encoding="utf-8")
        print(f"\U0001f4cc {BASELINE.relative_to(ROOT)} : instantané de référence créé")
        return True

    before = [line.partition("|")[2] for line in BASELINE.read_text(encoding="utf-8").splitlines()]
    if before == entries:
        return True

    print("\u274c La liste des textes français a changé : les traductions risquent d'être décalées.")
    for index in range(max(len(before), len(entries))):
        old_value = before[index] if index < len(before) else None
        new_value = entries[index] if index < len(entries) else None
        if old_value != new_value:
            print(f"   index {index}")
            print(f"     avant : {old_value!r}")
            print(f"     après : {new_value!r}")
    if accept:
        BASELINE.write_text(printed + "\n", encoding="utf-8")
        print("\u26a0\ufe0f  Instantané mis à jour (--accept) : vérifiez l'alignement dans reference.md.")
        return True
    print("   \u2192 remettez les traductions en face des bons textes, puis relancez avec --accept.")
    return False


def main() -> int:
    check = "--check" in sys.argv
    html = INDEX.read_text(encoding="utf-8")
    master, meta_texts = extract_master_list(html)
    entries = master + meta_texts + RUNTIME_STRINGS

    if "--dump" in sys.argv:
        for i, value in enumerate(entries):
            print(f"{i:>3}|{value}")
        return 0

    if not check_baseline(entries, "--accept" in sys.argv):
        return 1

    langs: dict[str, dict[str, str]] = {}
    problems: list[str] = []
    for code, path in LANGS.items():
        lines, missing = load_lines(path, len(entries))
        if path.exists() and missing:
            left = [i for i in missing if any(c.isalpha() for c in entries[i])]
            detail = ", ".join(str(i) for i in missing[:15])
            problems.append(
                f"{path.name} : {len(missing)} texte(s) sans traduction, dont {len(left)} "
                f"avec des mots (index {detail}{'…' if len(missing) > 15 else ''})"
            )
        mapping: dict[str, str] = {}
        for fr, tr in zip(entries, lines):
            tr = tr.strip()
            if not tr or tr == "-" or tr == fr:
                continue
            mapping[fr] = tr
        langs[code] = mapping

    payload = {
        "fr": entries,
        "translations": langs,
        "metaCount": len(meta_texts),
    }
    body = json.dumps(payload, ensure_ascii=False, indent=1)
    js = (
        "/* Généré par tools/i18n_build.py — ne pas modifier à la main.\n"
        "   Traductions à saisir dans tools/i18n/translations-en.txt et translations-wo.txt. */\n"
        f"window.AMAL_I18N_DATA = {body};\n"
    )

    coverage = " · ".join(f"{code.upper()} {len(mapping)}/{len(entries)}" for code, mapping in langs.items())

    if check:
        if OUT_JS.exists() and OUT_JS.read_text(encoding="utf-8") != js:
            print("❌ i18n-data.js n'est pas à jour : relancez sans --check.", file=sys.stderr)
            return 1
        # Les textes non traduits sont attendus : noms propres, téléphones, unités.
        # L'information est affichée mais ne fait pas échouer le contrôle.
        for problem in problems:
            print(f"ℹ️  {problem}")
        print(f"✅ À jour : {len(entries)} textes ({coverage}).")
        return 0

    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text(js, encoding="utf-8")

    rows = ["# Référence des traductions AMAL", "",
            "| # | Français (index.html) | English | Wolof |", "|---|---|---|---|"]
    for i, fr in enumerate(entries):
        en = langs["en"].get(fr, "—")
        wo = langs["wo"].get(fr, "—")
        esc = lambda s: s.replace("|", "\\|")  # noqa: E731
        rows.append(f"| {i} | {esc(fr)} | {esc(en)} | {esc(wo)} |")
    OUT_DOC.write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"✅ {OUT_JS.relative_to(ROOT)} : {len(entries)} textes ({coverage})")
    print(f"✅ {OUT_DOC.relative_to(ROOT)} : table de référence générée")
    for problem in problems:
        print(f"ℹ️  {problem}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
