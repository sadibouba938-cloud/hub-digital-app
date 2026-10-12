#!/usr/bin/env python3
"""Assemble le PDF de présentation du site vitrine AMAL.

À quoi ça sert
--------------
Produire un document à transmettre au client (ou à imprimer) à partir des
captures d'écran du site : page de couverture, vue d'ensemble, une page par
section, puis la liste des informations à confirmer avant publication.

Dépendances
-----------
``fpdf2`` et les polices DejaVu (présentes sur la plupart des systèmes Linux) :

    python3 -m venv /tmp/venv-pdf
    /tmp/venv-pdf/bin/pip install fpdf2
    /tmp/venv-pdf/bin/python tools/presentation_pdf.py captures/ presentation-amal.pdf

Les images sont générées par ailleurs (captures d'écran du site) ; ce script ne
dépend d'aucun navigateur.
"""
from __future__ import annotations

import sys
from pathlib import Path

from fpdf import FPDF

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
NAVY = (11, 31, 69)
BLUE = (27, 79, 216)
GREEN = (18, 148, 90)
GOLD = (242, 178, 51)
MUTED = (96, 112, 138)
LIGHT = (238, 242, 248)

TITLE = "AMAL — Détergents du Sénégal"
SUBTITLE = "Site vitrine : présentation des écrans"

# Une page par écran : (fichier, titre, commentaire)
PAGES = [
    ("01-hero-fr.png", "Accueil — version française (référence)",
     "Accroche, visuels d'atelier, compteurs de production et appels à l'action. "
     "Les prix affichent « à venir » : aucun tarif définitif n'est publié."),
    ("08-hero-wo.png", "Accueil — version wolof",
     "Le sélecteur FR · EN · WO bascule la page sans rechargement. Un bandeau rappelle "
     "que la version française fait foi, et l'adresse devient partageable (?lang=wo)."),
    ("07-hero-en.png", "Accueil — version anglaise",
     "Même page, textes traduits : l'anglais et le wolof sont des variantes du français, "
     "qui reste la langue de référence."),
    ("02-produits-fr.png", "La gamme AMAL — rendus 3D",
     "Huit références présentées en rendu 3D, toutes étiquetées AMAL, filtrables par "
     "catégorie (entretien maison, lessive, hygiène, professionnel)."),
    ("03-formats-fr.png", "Formats disponibles",
     "Du flacon familial au bidon professionnel, avec le packshot duo 5 L + 1 L. "
     "Les contenances sont annoncées, les prix restent « à venir »."),
    ("04-services-fr.png", "Services — un partenaire industriel",
     "Production à façon (marque blanche), vente en gros et vrac, livraison nationale, "
     "formulation sur mesure et programme revendeurs."),
    ("05-equipe-fr.png", "Notre histoire — visuel d'équipe",
     "L'équipe AMAL à Diamniadio avec la gamme, à côté du récit de marque et des chiffres clés."),
    ("06-devis-fr.png", "Formulaire de devis",
     "Demande qualifiée (type de besoin, volume estimé, zone de livraison) envoyée via "
     "WhatsApp ou par e-mail, avec un récapitulatif construit côté navigateur."),
    ("09-mobile-fr.png", "Affichage mobile",
     "Le site est pensé pour le téléphone : menu compact, sections empilées et bouton "
     "WhatsApp toujours accessible."),
]

CHECKLIST = [
    "Coordonnées réelles : téléphone, WhatsApp, e-mail professionnel et adresse de l'usine",
    "Numéro NINEA et mentions légales définitives",
    "Prix publics, formats commercialisables et quantités minimum",
    "Zones et délais de livraison réellement assurés",
    "Témoignages clients à recueillir (avec accord écrit) ou à retirer",
    "Validation des rendus 3D et des visuels d'usine par le client",
    "Nom de domaine et mise en ligne définitive",
    "Relecture de la version wolof par un locuteur natif",
]



def image_size(path: Path) -> tuple[int, int]:
    """Dimensions (largeur, hauteur) d'un PNG ou JPEG, en lisant l'en-tête."""
    import struct

    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    index = 2
    while index < len(data) - 9:
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB,
                      0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[index + 5:index + 9])
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            index += 2
            continue
        index += 2 + struct.unpack(">H", data[index + 2:index + 4])[0]
    raise ValueError(f"format d'image non reconnu : {path}")


class Deck(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(False)
        self.set_margins(16, 14, 16)
        self.add_font("DejaVu", "", str(FONT_DIR / "DejaVuSans.ttf"))
        self.add_font("DejaVu", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))
        self.page_no_hint = ""

    # --- éléments d'habillage -------------------------------------------
    def band(self, height: float = 5) -> None:
        """Bandeau supérieur bleu → vert, signature visuelle AMAL."""
        width = self.w - self.l_margin * 2
        for i in range(60):
            ratio = i / 59
            color = tuple(
                round(NAVY[c] + (GREEN[c] - NAVY[c]) * ratio) for c in range(3)
            )
            self.set_fill_color(*color)
            self.rect(self.l_margin + width * i / 60, self.t_margin - 4,
                      width / 60 + 0.4, height, "F")

    def place_image(self, name: str, x: float, y: float, max_w: float, max_h: float) -> None:
        """Insère l'image en respectant un cadre maximal (pas de débordement)."""
        path = self.images.get(name)
        if not path:
            return
        width, height = image_size(path)
        scale = min(max_w / width, max_h / height)
        self.image(str(path), x=x + (max_w - width * scale) / 2, y=y,
                   w=width * scale)

    def footer_text(self, text: str, page: str = "") -> None:
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*MUTED)
        self.set_y(-14)
        self.cell(0, 5, text, align="L")
        if page:
            self.set_x(self.w - self.r_margin - 40)
            self.cell(40, 5, page, align="R")

    # --- pages -----------------------------------------------------------
    def cover(self) -> None:
        self.add_page()
        self.set_fill_color(*NAVY)
        self.rect(0, 0, self.w, self.h, "F")
        self.band(4)

        self.set_y(36)
        self.set_font("DejaVu", "B", 34)
        self.set_text_color(255, 255, 255)
        self.cell(0, 14, "AMAL", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 15)
        self.set_text_color(*GOLD)
        self.cell(0, 9, "Détergents & produits d'hygiène — Sénégal",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_font("DejaVu", "B", 19)
        self.set_text_color(255, 255, 255)
        self.cell(0, 11, SUBTITLE, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 11)
        self.set_text_color(190, 205, 230)
        self.cell(0, 7, "Versions française · anglaise · wolof",
                  align="C", new_x="LMARGIN", new_y="NEXT")

        # Vignette d'accueil (cadrée entre le titre et la mention de bas de page)
        self.place_image("01-hero-fr.png", self.l_margin, 92,
                         self.w - self.l_margin * 2, 86)

        self.set_y(self.h - 26)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(170, 188, 220)
        self.cell(0, 5, "Maquette — prix et informations commerciales à confirmer "
                        "avant publication", align="C")

    def overview(self) -> None:
        self.add_page()
        self.band()
        self.set_y(20)
        self.set_font("DejaVu", "B", 20)
        self.set_text_color(*NAVY)
        self.cell(0, 10, "Le site en un coup d'œil", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 5.5, new_x="LMARGIN", new_y="NEXT", text="Page unique responsive, sans dépendance externe : "
                                "en-tête, gamme, formats, services, qualité, livraison, "
                                "témoignages, FAQ et formulaire de devis.")
        self.ln(3)
        sheet = "planche-amal.jpg" if "planche-amal.jpg" in self.images else "planche-amal.png"
        self.place_image(sheet, self.l_margin, self.get_y() - 1,
                         self.w - self.l_margin - self.r_margin,
                         self.h - self.get_y() - 18)
        self.footer_text("AMAL — présentation du site vitrine", "1")

    def screen(self, name: str, title: str, comment: str, page_no: int) -> None:
        self.add_page()
        self.band()
        self.set_y(19)
        self.set_font("DejaVu", "B", 15)
        self.set_text_color(*NAVY)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 9.5)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 5, comment, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.place_image(name, self.l_margin, self.get_y(),
                         self.w - self.l_margin - self.r_margin,
                         self.h - self.get_y() - 16)

        self.footer_text("AMAL — présentation du site vitrine", str(page_no))

    def checklist(self, page_no: int) -> None:
        self.add_page()
        self.band()
        self.set_y(19)
        self.set_font("DejaVu", "B", 17)
        self.set_text_color(*NAVY)
        self.cell(0, 10, "À confirmer avant la mise en ligne",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 5.5, new_x="LMARGIN", new_y="NEXT", text="La maquette contient volontairement des informations "
                                "provisoires. Les prix et les détails commerciaux restent "
                                "« à venir » et ne sont publiés qu'après validation.")
        self.ln(4)
        self.set_text_color(*NAVY)
        for item in CHECKLIST:
            self.set_font("DejaVu", "B", 10)
            self.set_text_color(*GREEN)
            self.cell(7, 7, "✓")
            self.set_font("DejaVu", "", 10)
            self.set_text_color(40, 55, 80)
            self.multi_cell(0, 7, item, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*NAVY)
        self.cell(0, 6, "Comment activer les prix plus tard",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 9.5)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 5.2, new_x="LMARGIN", new_y="NEXT", text="Les mentions « Prix à venir » sont balisées dans le code "
                                "(classe .soon) : le remplacement par les tarifs définitifs "
                                "ne demande aucune refonte de la page. Les procédures de "
                                "traduction et de mise à jour sont décrites dans le README "
                                "du dossier site-vitrine-amal.")
        self.footer_text("AMAL — présentation du site vitrine", str(page_no))


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    source, target = Path(sys.argv[1]), Path(sys.argv[2])
    images = {path.name: path for path in source.glob("*") if path.suffix.lower() in {".png", ".jpg"}}
    missing = [name for name, _, _ in PAGES if name not in images]
    if missing:
        print("⚠️  captures manquantes :", ", ".join(missing))

    pdf = Deck()
    pdf.images = images
    pdf.cover()
    pdf.overview()
    for index, (name, title, comment) in enumerate(PAGES, start=2):
        pdf.screen(name, title, comment, index)
    pdf.checklist(len(PAGES) + 2)

    pdf.set_title(f"{TITLE} — {SUBTITLE}")
    pdf.set_author("AMAL — Détergents du Sénégal")
    pdf.output(str(target))
    print(f"✅ {target} — {pdf.pages_count} pages, {round(target.stat().st_size / 1024)} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
