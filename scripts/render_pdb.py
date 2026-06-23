#!/usr/bin/env python3
"""
render_pdb.py — Render a modern-format President's Daily Brief PDF.

Takes a JSON file describing the day's brief and produces a PDF whose layout
matches the modern (post-2010s) declassified PDB house style:

  - TOP SECRET//NOFORN classification banner, centered, top AND bottom of every page
  - A White House line-engraving in the top-right + a red diagonal corner flash
  - "For the President" / spelled-out date, italic, top-left, under a thin rule
  - Each article: a bold headline, a lead assessment paragraph, then bulleted
    sub-assessments. Articles may carry "* * *" (rendered as star glyphs) dividers
    and end with an italic "Prepared by ..." source line.
  - "Continued . . ." italic at the foot of any page an article spills past.

Usage:
    python render_pdb.py brief.json out.pdf

See references/brief_schema.md for the JSON shape. Run with --sample to drop a
sample brief.json next to the script and render it, which is handy for eyeballing
the format.
"""

import sys
import json
import os
import datetime

from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.colors import Color, black, white, HexColor
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    ListFlowable, ListItem, FrameBreak, KeepTogether, Flowable,
    NextPageTemplate, PageBreak,
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas as canvas_mod
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----------------------------------------------------------------------------
# Fonts — the modern PDB is set in Calibri. We register Carlito, the
# metric-compatible open clone of Calibri, so the document matches the real
# typeface. Font files are looked for (in order) in the skill's assets/fonts,
# then common system locations. If none are found we fall back to Helvetica.
# ----------------------------------------------------------------------------
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"
FONT_BOLDITALIC = "Helvetica-BoldOblique"
# Condensed faces used on the SCI cover sheet markings (real sheets use a
# condensed bold sans). Falls back to Helvetica-Bold if unavailable.
FONT_COND_BOLD = "Helvetica-Bold"
FONT_COVER_BODY = "Helvetica-Bold"  # caveat/handling text on the cover


def _register_fonts():
    global FONT_REGULAR, FONT_BOLD, FONT_ITALIC, FONT_BOLDITALIC
    here = os.path.dirname(os.path.abspath(__file__))
    search = [
        os.path.normpath(os.path.join(here, "..", "assets", "fonts")),
        "/usr/share/fonts/truetype/crosextra",
        "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
        "/usr/share/fonts", "C:/Windows/Fonts",
    ]
    variants = {
        "Carlito": "Carlito-Regular.ttf",
        "Carlito-Bold": "Carlito-Bold.ttf",
        "Carlito-Italic": "Carlito-Italic.ttf",
        "Carlito-BoldItalic": "Carlito-BoldItalic.ttf",
    }
    # Also accept real Calibri if present (preferred — it's the exact face).
    calibri = {
        "Carlito": "calibri.ttf", "Carlito-Bold": "calibrib.ttf",
        "Carlito-Italic": "calibrii.ttf", "Carlito-BoldItalic": "calibriz.ttf",
    }
    found = {}
    for name, fname in variants.items():
        for d in search:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                found[name] = p
                break
        if name not in found:  # try Calibri filename in same dirs
            for d in search:
                p = os.path.join(d, calibri[name])
                if os.path.exists(p):
                    found[name] = p
                    break
    if len(found) == 4:
        try:
            for name, p in found.items():
                pdfmetrics.registerFont(TTFont(name, p))
            pdfmetrics.registerFontFamily(
                "Carlito", normal="Carlito", bold="Carlito-Bold",
                italic="Carlito-Italic", boldItalic="Carlito-BoldItalic")
            FONT_REGULAR, FONT_BOLD = "Carlito", "Carlito-Bold"
            FONT_ITALIC, FONT_BOLDITALIC = "Carlito-Italic", "Carlito-BoldItalic"
        except Exception:
            pass  # keep Helvetica fallback

    # Condensed faces for the SCI cover markings.
    global FONT_COND_BOLD, FONT_COVER_BODY
    cond_files = {
        "SansNarrow-Bold": "LiberationSansNarrow-Bold.ttf",
        "Sans-Bold": "LiberationSans-Bold.ttf",
    }
    cond_dirs = [
        os.path.normpath(os.path.join(here, "..", "assets", "fonts")),
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype/liberation2",
        "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
    ]
    for fontname, fname in cond_files.items():
        for d in cond_dirs:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(fontname, p))
                except Exception:
                    pass
                break
    # Use them if registration succeeded.
    try:
        pdfmetrics.getFont("SansNarrow-Bold")
        FONT_COND_BOLD = "SansNarrow-Bold"
    except Exception:
        FONT_COND_BOLD = FONT_BOLD
    try:
        pdfmetrics.getFont("Sans-Bold")
        FONT_COVER_BODY = "Sans-Bold"
    except Exception:
        FONT_COVER_BODY = FONT_BOLD


_register_fonts()

# ----------------------------------------------------------------------------
# Palette / constants
# ----------------------------------------------------------------------------
RED = HexColor("#9E1B1B")          # corner flash + (optional) release stamp
INK = HexColor("#1a1a1a")
GREY_RULE = HexColor("#9a9a9a")
STAR_GREY = HexColor("#b0b0b0")

PAGE_W, PAGE_H = letter
LMARGIN = 0.85 * inch
RMARGIN = 0.80 * inch
TMARGIN = 1.05 * inch              # banner sits above; story masthead band starts here
BMARGIN = 0.95 * inch              # leaves room for footer banner

CLASSIFICATION = "TOP SECRET//NOFORN"   # overridable via brief["classification"]
SHORT_CLASS = "TOP SECRET"              # the short marking that sits by the date

# ----------------------------------------------------------------------------
# Styles
# ----------------------------------------------------------------------------
def build_styles():
    ss = getSampleStyleSheet()
    styles = {}
    styles["header_label"] = ParagraphStyle(
        "header_label", parent=ss["Normal"], fontName=FONT_ITALIC,
        fontSize=10.5, leading=14, textColor=INK,
    )
    styles["headline"] = ParagraphStyle(
        "headline", parent=ss["Normal"], fontName=FONT_BOLD,
        fontSize=12, leading=14.5, spaceBefore=1, spaceAfter=6, textColor=INK,
    )
    styles["body"] = ParagraphStyle(
        "body", parent=ss["Normal"], fontName=FONT_REGULAR,
        fontSize=9, leading=11.5, spaceAfter=5, textColor=INK,
        alignment=TA_LEFT,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=styles["body"], leftIndent=4, spaceAfter=4,
    )
    styles["prepared"] = ParagraphStyle(
        "prepared", parent=ss["Normal"], fontName=FONT_ITALIC,
        fontSize=8.5, leading=11, spaceBefore=7, spaceAfter=4, textColor=INK,
    )
    styles["cover_title"] = ParagraphStyle(
        "cover_title", parent=ss["Normal"], fontName=FONT_BOLD,
        fontSize=26, leading=30, alignment=TA_LEFT, textColor=INK,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", parent=ss["Normal"], fontName=FONT_REGULAR,
        fontSize=13, leading=18, alignment=TA_LEFT, textColor=INK,
    )
    styles["toc_head"] = ParagraphStyle(
        "toc_head", parent=ss["Normal"], fontName=FONT_BOLD,
        fontSize=12, leading=16, spaceAfter=10, textColor=INK,
    )
    styles["toc_item"] = ParagraphStyle(
        "toc_item", parent=ss["Normal"], fontName=FONT_REGULAR,
        fontSize=11.5, leading=16, spaceAfter=8, textColor=INK,
    )
    return styles


# ----------------------------------------------------------------------------
# Page furniture (drawn on every page via onPage callbacks)
# ----------------------------------------------------------------------------
_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def _emblem_path(brief=None):
    """Resolve the White House emblem image. Precedence:
    1) brief['emblem'] if provided (lets the user point at their exact 'IC' file)
    2) assets/whitehouse.png bundled with the skill
    Returns None if nothing is found (renderer then skips the emblem)."""
    if brief and brief.get("emblem"):
        p = brief["emblem"]
        if os.path.exists(p):
            return p
    cand = os.path.normpath(os.path.join(_ASSET_DIR, "whitehouse.png"))
    return cand if os.path.exists(cand) else None


def draw_white_house(c, emblem_path, center_x, top_y, draw_w=1.35 * inch):
    """Place the White House emblem image, centered horizontally on center_x,
    with its top at top_y. Sized to ~1.35in wide to match the real PDB header
    mark. Aspect ratio is read from the image so it never distorts."""
    if not emblem_path:
        return
    try:
        img = ImageReader(emblem_path)
        iw, ih = img.getSize()
        draw_h = draw_w * (ih / float(iw))
        x = center_x - draw_w / 2.0
        y = top_y - draw_h
        c.drawImage(img, x, y, width=draw_w, height=draw_h,
                    mask="auto", preserveAspectRatio=True)
    except Exception:
        pass  # never let a bad image kill the render


def draw_red_corner(c):
    """Solid red right-triangle flash in the very top-right corner — the printed
    classification corner marking the real PDB carries (a flat flag, not a fold)."""
    c.saveState()
    c.setFillColor(RED)
    s = 0.80 * inch
    p = c.beginPath()
    p.moveTo(PAGE_W, PAGE_H)
    p.lineTo(PAGE_W - s, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H - s)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


# Colors for the SCI cover sheet. The reference Standard Form is red; the user
# wants the same layout in a gold tone. Both the border band and the text use
# this single color, like the real form.
COVER_INK = HexColor("#C8A12C")     # goldish — border band + all text
COVER_YELLOW = COVER_INK            # (border uses the same gold)


def draw_sci_cover(c, brief):
    """Paint the SCI cover sheet to the EXACT geometry of the genuine Standard
    Form (measured from the reference PDF, page 612x792 pt), recolored to gold.
    Layout (positions are pt-from-top of the Letter page):

      border:    18 pt outer margin, ~37 pt band thickness
      big mark:  ~90 pt (top) and ~632 pt (bottom), centered, ~30 pt bold
      compartment line ~176 pt, centered
      THIS IS A COVER SHEET ~226 pt; FOR CLASSIFIED INFORMATION ~254 pt
      caveat blocks (left-aligned) starting ~294 pt and ~350 pt
      (This cover sheet is unclassified.) ~584 pt, centered

    All coordinates are taken directly from the reference so the result matches
    its dimensions; only the wording (TOP SECRET//SCI coversheet text) and the
    color (gold) differ."""
    from reportlab.platypus import Paragraph as _P
    from reportlab.lib.enums import TA_LEFT as _TL

    top_marking = brief.get("cover_marking", "TOP SECRET//SCI")
    compartments = brief.get(
        "cover_compartments",
        "CONTAINS SENSITIVE COMPARTMENTED INFORMATION<br/>UP TO HCS-P/SI/TK",
    )

    cx = PAGE_W / 2.0

    # Work directly in points (PAGE_H is in points). Y() maps pt-from-top -> baseline.
    def Y(pt_from_top):
        return PAGE_H - pt_from_top

    # ----- gold border frame (outer margin 18pt, band ~37pt) -----
    margin = 18.0
    border = 37.0
    c.saveState()
    c.setFillColor(COVER_INK)
    c.rect(margin, margin, PAGE_W - 2 * margin, PAGE_H - 2 * margin, fill=1, stroke=0)
    c.setFillColor(white)
    c.rect(margin + border, margin + border,
           PAGE_W - 2 * (margin + border), PAGE_H - 2 * (margin + border),
           fill=1, stroke=0)
    c.restoreState()

    # interior left margin for the left-aligned caveats (measured L≈85 pt)
    cav_left = 85.0
    cav_right = 527.0           # measured caveats run to ~527 pt
    cav_w = cav_right - cav_left

    def gold_center(top_pt, text, font, size, leading=None):
        """Centered gold text at a baseline; supports <br/>. top_pt is the
        baseline position in points-from-top. Returns next baseline (pt-from-top)."""
        c.setFillColor(COVER_INK)
        c.setFont(font, size)
        ld = leading if leading else size * 1.3
        yt = top_pt
        for ln in text.replace("<br/>", "\n").split("\n"):
            c.drawCentredString(cx, Y(yt), ln)
            yt += ld
        return yt

    def gold_caveat(top_pt, text, font, size, leading):
        """Left-aligned, JUSTIFIED gold paragraph in the measured caveat column.
        top_pt is the top of the block in pt-from-top. Returns bottom pt-from-top."""
        from reportlab.lib.enums import TA_JUSTIFY
        st = ParagraphStyle("cv", fontName=font, fontSize=size, leading=leading,
                            alignment=TA_JUSTIFY, textColor=COVER_INK)
        p = _P(text, st)
        w, h = p.wrap(cav_w, 4 * inch)
        p.drawOn(c, cav_left, Y(top_pt) - h)
        return top_pt + h / 1.0  # bottom in pt-from-top (h already in pts)

    # ===== exact-position elements =====
    # Big top marking — baseline ~ top 90 + cap height; place baseline at 120 pt.
    gold_center(120.0, top_marking, FONT_BOLD, 30)

    # Compartment line — top ~176 pt; baseline ~187. Two lines, leading 16.
    gold_center(187.0, compartments, FONT_BOLD, 11, leading=16)

    # THIS IS A COVER SHEET — top ~226 pt; baseline ~234.
    gold_center(234.0, "THIS IS A COVER SHEET", FONT_BOLD, 10.5)

    # FOR CLASSIFIED INFORMATION — top ~254 pt; baseline ~262.
    gold_center(262.0, "FOR CLASSIFIED INFORMATION", FONT_BOLD, 10.5)

    # Caveat 1 — block starts ~294 pt (left-aligned, justified).
    cav1 = ("ALL INDIVIDUALS HANDLING THIS INFORMATION ARE REQUIRED TO "
            "PROTECT IT FROM UNAUTHORIZED DISCLOSURE IN THE INTEREST OF THE "
            "NATIONAL SECURITY OF THE UNITED STATES.")
    bottom1 = gold_caveat(294.0, cav1, FONT_BOLD, 9, 14)

    # Caveat 2 — block starts ~350 pt.
    cav2 = ("HANDLING, STORAGE, REPRODUCTION AND DISPOSITION OF THE "
            "ATTACHED DOCUMENT MUST BE IN ACCORDANCE WITH APPLICABLE "
            "EXECUTIVE ORDERS, STATUTES AND AGENCY IMPLEMENTING REGULATIONS.")
    gold_caveat(350.0, cav2, FONT_BOLD, 9, 14)

    # (This cover sheet is unclassified.) — ~584 pt, centered.
    gold_center(590.0, "(This cover sheet is unclassified.)", FONT_BOLD, 9)

    # Big bottom marking — baseline ~ top 632 + cap height; baseline at 662 pt.
    gold_center(662.0, top_marking, FONT_BOLD, 30)

    # ----- form footer (small print, like the SF-7), in gold -----
    foot = brief.get("cover_footer_left", "PDB 1–1–1")
    foot_mid = brief.get("cover_footer_mid", "")
    foot_right = brief.get("cover_footer_right",
                           "OFFICE OF THE DIRECTOR OF NATIONAL INTELLIGENCE")
    c.setFillColor(COVER_INK)
    c.setFont(FONT_BOLD, 7.5)
    foot_y = Y(720.0)
    c.drawString(cav_left, foot_y, foot)
    if foot_mid:
        c.drawCentredString(cx, foot_y, foot_mid)
    c.drawRightString(PAGE_W - margin - border - 18, foot_y, foot_right)


def draw_banner(c, y, text):
    """Centered classification banner."""
    c.saveState()
    c.setFont(FONT_BOLD, 11)
    c.setFillColor(black)
    c.drawCentredString(PAGE_W / 2.0, y, text)
    c.restoreState()


def make_on_page(classification, short_class, release_stamp=None,
                 cover_pages=(), article_end_pages=None, total_pages=None,
                 emblem_path=None, story_start_pages=None):
    """Returns an onPage callback that paints banners + corner, draws the White
    House emblem at the TOP OF EACH STORY (its first page only), and stamps
    'Continued . . .' on any content page that is not an article's last page.
    article_end_pages and story_start_pages are sets discovered in a first build
    pass; on that pass they're None, so nothing page-dependent is drawn yet."""
    def _on_page(c, doc):
        pg = c.getPageNumber()
        is_cover = pg in cover_pages
        # top + bottom classification banners (every page incl. cover)
        draw_banner(c, PAGE_H - 0.62 * inch, classification)
        draw_banner(c, 0.62 * inch, classification)
        # red corner flash on every page.
        draw_red_corner(c)
        # NOTE: the White House emblem is NOT drawn here. It is part of the
        # masthead HeaderBlock that leads each story, so it sits inline with the
        # 'For the President' / date line above the rule — matching the real PDB.
        # optional faint release stamp (off by default per user request)
        if release_stamp:
            c.saveState()
            c.setFont("Courier-Bold", 12)
            c.setFillColor(RED)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - 0.40 * inch, release_stamp)
            c.restoreState()
        # 'Continued . . .' footer: any content page that isn't an article's
        # final page (and isn't the cover, and isn't the document's last page).
        if (article_end_pages is not None and not is_cover
                and pg not in article_end_pages
                and (total_pages is None or pg != total_pages)):
            c.saveState()
            c.setFont(FONT_ITALIC, 11)
            c.setFillColor(INK)
            c.drawRightString(PAGE_W - RMARGIN, BMARGIN - 0.30 * inch, "Continued . . .")
            c.restoreState()
        # ★ ★ ★ at the top of a CONTINUATION page — a content page where a story
        # is spilling over from the previous page (i.e. not the cover and not a
        # story-start page). This is the real PDB's cue that the reader is picking
        # up a continued story, and it makes the star divider feature naturally.
        if (story_start_pages is not None and not is_cover
                and pg not in story_start_pages):
            # Match the real PDB: a faint full-width rule with the three stars
            # sitting just below it (same as the in-body divider).
            star_y = PAGE_H - 1.10 * inch
            rule_y = star_y + 0.20 * inch
            c.saveState()
            c.setStrokeColor(GREY_RULE)
            c.setLineWidth(0.6)
            c.line(LMARGIN, rule_y, PAGE_W - RMARGIN, rule_y)
            c.restoreState()
            _draw_three_stars(c, PAGE_W / 2.0, star_y,
                              size=5.0, gap=14.0, color=STAR_GREY)
    return _on_page


def _draw_three_stars(c, cx, cy, size=5.0, gap=14.0, color=None):
    """Draw a centered '★ ★ ★' as three filled five-point star polygons, so the
    divider renders identically regardless of font glyph coverage."""
    import math
    if color is None:
        color = HexColor("#7a7a7a")
    c.saveState()
    c.setFillColor(color)
    centers = [cx - gap, cx, cx + gap]
    for sx in centers:
        p = c.beginPath()
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5     # start pointing up
            r = size if i % 2 == 0 else size * 0.42
            x = sx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            if i == 0:
                p.moveTo(x, y)
            else:
                p.lineTo(x, y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


# ----------------------------------------------------------------------------
# Custom flowables
# ----------------------------------------------------------------------------
class StarRule(Flowable):
    """A centered '* * *' rendered as three small stars, sitting under a faint
    full-width rule — matches the section divider in the reference images."""
    def __init__(self, width, rule=True):
        super().__init__()
        self.width = width
        self.rule = rule
        self.height = 24

    def draw(self):
        c = self.canv
        if self.rule:
            c.setStrokeColor(GREY_RULE)
            c.setLineWidth(0.6)
            c.line(0, self.height - 2, self.width, self.height - 2)
        c.setFillColor(STAR_GREY)
        c.setFont(FONT_REGULAR, 12)
        c.drawCentredString(self.width / 2.0, 2, "★ ★ ★")


class HeaderBlock(Flowable):
    """The masthead band that opens each story's first page, matching the real
    PDB: 'For the President' + date in italics on the LEFT, the White House
    emblem on the RIGHT, both vertically centered on the same row, with a thin
    full-width rule running underneath both. The emblem is sized and centered
    against the two-line text so the whole band reads as one unit."""
    def __init__(self, width, date_str, label="For the President",
                 emblem_path=None, emblem_w=1.275 * inch):
        super().__init__()
        self.width = width
        self.date_str = date_str
        self.label = label
        self.emblem_path = emblem_path
        self.emblem_w = emblem_w
        # Band tall enough to seat the emblem; the text sits centered within it.
        self._emblem_h = 0.0
        if emblem_path:
            try:
                iw, ih = ImageReader(emblem_path).getSize()
                self._emblem_h = emblem_w * (ih / float(iw))
            except Exception:
                self._emblem_h = 0.0
        # Header band height: a touch taller than the emblem, with room for the rule.
        self.height = max(0.62 * inch, self._emblem_h + 0.14 * inch)

    def draw(self):
        c = self.canv
        rule_y = 2.0
        band_top = self.height
        mid = (rule_y + band_top) / 2.0  # vertical center of the band

        # ----- Emblem, right-aligned, vertically centered on the band -----
        if self.emblem_path and self._emblem_h:
            try:
                img = ImageReader(self.emblem_path)
                x = self.width - self.emblem_w
                y = mid - self._emblem_h / 2.0
                c.drawImage(img, x, y, width=self.emblem_w, height=self._emblem_h,
                            mask="auto", preserveAspectRatio=True)
            except Exception:
                pass

        # ----- 'For the President' / date, left, centered on the same band -----
        c.setFillColor(INK)
        c.setFont(FONT_ITALIC, 10.5)
        line_gap = 14
        # center the two-line text block on `mid`
        first_y = mid + line_gap / 2.0 - 4
        c.drawString(0, first_y, self.label)
        c.drawString(0, first_y - line_gap, self.date_str)

        # ----- Full-width rule beneath both -----
        c.setStrokeColor(GREY_RULE)
        c.setLineWidth(0.8)
        c.line(0, rule_y, self.width, rule_y)


class ArticleEndMarker(Flowable):
    """Zero-height marker placed at the end of each article. During build it
    records the page number on which the article finished, so the footer logic
    can stamp 'Continued . . .' on every page that is NOT an article's last page."""
    def __init__(self, registry):
        super().__init__()
        self.registry = registry
        self.width = 0
        self.height = 0

    def draw(self):
        self.registry.add(self.canv.getPageNumber())


class StoryStartMarker(Flowable):
    """Zero-height marker placed immediately before an article's headline. During
    the build it records the page number the article *begins* on, so the emblem
    is drawn only at the top of each story (its first page) — not on continuation
    pages. Placed after any FrameBreak so the recorded page is the headline's."""
    def __init__(self, registry):
        super().__init__()
        self.registry = registry
        self.width = 0
        self.height = 0

    def draw(self):
        self.registry.add(self.canv.getPageNumber())


# ----------------------------------------------------------------------------
# Document assembly
# ----------------------------------------------------------------------------
def spell_date(date_str):
    """Accept YYYY-MM-DD or already-spelled; return 'DD Month YYYY' (day-first,
    matching the reference images: '14 September 2016')."""
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return d.strftime("%-d %B %Y")
    except ValueError:
        return date_str


def cover_date(date_str):
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return d.strftime("%-d %B %Y")
    except ValueError:
        return date_str


def _make_story(brief, styles, content_w, date_str, date_spelled, end_registry,
                start_registry=None):
    """Assemble the flowable story. end_registry is a set that ArticleEndMarker
    populates with article-final page numbers; start_registry (if given) is a set
    that StoryStartMarker populates with each article's first page number."""
    if start_registry is None:
        start_registry = set()
    story = []
    cover = brief.get("cover", True)
    toc = brief.get("toc")

    # ----- SCI cover sheet -----
    # The cover is the user's own PDF (assets/cover.pdf), prepended verbatim by
    # the build step AFTER content is rendered. We deliberately do NOT emit any
    # cover page here, so the content starts on page 1 of the inner document and
    # the real cover becomes page 1 of the merged output. (Nothing to do here.)

    # ----- Optional table of contents -----
    if toc:
        story.append(HeaderBlock(content_w, date_spelled))
        story.append(Spacer(1, 0.18 * inch))
        story.append(Paragraph("Today’s Brief", styles["toc_head"]))
        for entry in toc:
            tag = entry.get("tag", "").upper()
            summ = entry.get("summary", "")
            line = f"<b>{tag}:</b> {summ}" if tag else summ
            story.append(Paragraph(line, styles["toc_item"]))
        story.append(ArticleEndMarker(end_registry))  # ToC page counts as "complete"
        story.append(FrameBreak())

    # ----- Articles -----
    # Each story opens with the masthead band (For the President / date + emblem
    # + rule), exactly like the real PDB. The band leads each article's flow so
    # it sits at the top of that story's first page.
    articles = brief["articles"]
    emblem_path = _emblem_path(brief)
    for ai, art in enumerate(articles):
        flow = [
            StoryStartMarker(start_registry),
            HeaderBlock(content_w, date_spelled, emblem_path=emblem_path),
            Spacer(1, 0.22 * inch),
            Paragraph(art["headline"], styles["headline"]),
        ]
        for block in art["blocks"]:
            btype = block.get("type", "para")
            if btype == "para":
                flow.append(Paragraph(block["text"], styles["body"]))
            elif btype == "bullets":
                items = [
                    ListItem(Paragraph(t, styles["bullet"]), leftIndent=22,
                             bulletColor=INK)
                    for t in block["items"]
                ]
                flow.append(ListFlowable(
                    items, bulletType="bullet", start="•",
                    bulletFontName=FONT_REGULAR, bulletFontSize=11,
                    leftIndent=22, bulletOffsetY=-1,
                ))
                flow.append(Spacer(1, 4))
            elif btype == "stars":
                flow.append(Spacer(1, 4))
                flow.append(StarRule(content_w, rule=block.get("rule", True)))
                flow.append(Spacer(1, 4))
        prepared = art.get("prepared_by")
        # Keep the source line attached to the last content flowable so an
        # article never strands a lone "Prepared by …" on an otherwise empty
        # continuation page. We bind the final body flowable + the source line
        # (+ the end marker) together with KeepTogether.
        end_marker = ArticleEndMarker(end_registry)
        if prepared:
            prepared_flow = Paragraph(prepared, styles["prepared"])
            tail = flow.pop() if flow else None  # last content flowable
            if tail is not None:
                story.extend(flow)
                story.append(KeepTogether([tail, prepared_flow, end_marker]))
            else:
                story.append(KeepTogether([prepared_flow, end_marker]))
        else:
            flow.append(end_marker)
            story.extend(flow)

        if ai != len(articles) - 1:
            story.append(FrameBreak())
    return story


def _count_cover_pages(brief):
    return {1} if brief.get("cover", True) else set()


def build(brief, out_path):
    styles = build_styles()
    classification = brief.get("classification", CLASSIFICATION)
    short_class = brief.get("short_classification", SHORT_CLASS)
    release_stamp = brief.get("release_stamp")  # default None => omitted
    date_str = brief.get("date") or datetime.date.today().isoformat()
    date_spelled = spell_date(date_str)
    content_w = PAGE_W - LMARGIN - RMARGIN
    has_cover = brief.get("cover", True)
    emblem_path = _emblem_path(brief)
    # The cover is the user's own PDF, prepended verbatim after content renders.
    # So the inner (content) document has NO cover page: page 1 is the first story.
    cover_pages = set()

    # Content renders to a temp path when a cover will be prepended; otherwise
    # straight to out_path.
    import tempfile
    if has_cover:
        _fd, content_path = tempfile.mkstemp(suffix="_content.pdf")
        os.close(_fd)
    else:
        content_path = out_path

    def make_doc(on_page):
        frame = Frame(
            LMARGIN, BMARGIN, content_w, PAGE_H - TMARGIN - BMARGIN,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="main",
        )
        content_tmpl = PageTemplate(id="content", frames=[frame], onPage=on_page)
        d = BaseDocTemplate(
            content_path, pagesize=letter,
            leftMargin=LMARGIN, rightMargin=RMARGIN,
            topMargin=TMARGIN, bottomMargin=BMARGIN,
            title="The President's Daily Brief", author="ODNI (mock)",
        )
        d.addPageTemplates([content_tmpl])
        return d

    # ---- Pass 1: discover article-end pages, story-start pages, total count ----
    end_registry = set()
    start_registry = set()
    pass1_on_page = make_on_page(classification, short_class, release_stamp,
                                 cover_pages=cover_pages, article_end_pages=None,
                                 emblem_path=emblem_path, story_start_pages=None)
    doc1 = make_doc(pass1_on_page)
    story1 = _make_story(brief, styles, content_w, date_str, date_spelled,
                         end_registry, start_registry=start_registry)
    doc1.build(story1)
    total_pages = doc1.page

    # ---- Pass 2: emblem at each story's start; 'Continued . . .' on spill pages ----
    pass2_on_page = make_on_page(classification, short_class, release_stamp,
                                 cover_pages=cover_pages,
                                 article_end_pages=end_registry,
                                 total_pages=total_pages,
                                 emblem_path=emblem_path,
                                 story_start_pages=start_registry)
    doc2 = make_doc(pass2_on_page)
    story2 = _make_story(brief, styles, content_w, date_str, date_spelled, set(),
                         start_registry=set())
    doc2.build(story2)

    # ---- Prepend the user's cover PDF verbatim (page 1), then content ----
    if has_cover:
        cover_pdf = _cover_pdf_path(brief)
        try:
            from pypdf import PdfReader, PdfWriter
            writer = PdfWriter()
            if cover_pdf and os.path.exists(cover_pdf):
                for pg in PdfReader(cover_pdf).pages:
                    writer.add_page(pg)
            for pg in PdfReader(content_path).pages:
                writer.add_page(pg)
            with open(out_path, "wb") as fh:
                writer.write(fh)
        except Exception:
            # If merge fails for any reason, fall back to content-only output so
            # the brief is still produced.
            import shutil
            shutil.copyfile(content_path, out_path)
        finally:
            try:
                os.remove(content_path)
            except OSError:
                pass


def _cover_pdf_path(brief=None):
    """Resolve the cover PDF. Precedence: brief['cover_pdf'] if it exists, else
    the bundled assets/cover.pdf. Returns None if neither is present."""
    if brief and brief.get("cover_pdf") and os.path.exists(brief["cover_pdf"]):
        return brief["cover_pdf"]
    cand = os.path.normpath(os.path.join(_ASSET_DIR, "cover.pdf"))
    return cand if os.path.exists(cand) else None


# ----------------------------------------------------------------------------
# Sample brief (for --sample)
# ----------------------------------------------------------------------------
SAMPLE = {
    "date": "2016-09-14",
    "classification": "TOP SECRET//NOFORN",
    "short_classification": "TOP SECRET",
    "cover": True,
    "articles": [
        {
            "headline": "Cyber Threats to US Election Unlikely To Alter Voting Outcomes",
            "blocks": [
                {"type": "para", "text": "We assess that foreign adversaries do not have the capability to covertly overturn the vote outcome of the coming US presidential election by executing cyber attacks on election infrastructure. These adversaries—most notably Russia—can conduct cyber operations against election infrastructure to undermine the credibility of the process and weaken the perceived legitimacy of the winning candidate."},
                {"type": "bullets", "items": [
                    "Multiple checks and redundancies in the voting system make it likely that officials could detect a large-scale manipulation of election systems intended to change an outcome, especially in a well-covered US presidential election.",
                    "We assess that Russia has increased the aggressiveness of cyber capabilities used against US Government and political targets as demonstrated by recent high-profile operations against a national political party.",
                ]},
                {"type": "stars", "rule": True},
                {"type": "bullets", "items": [
                    "Nonstate cyber actors probably have the capability and intent to steal voter registration data, based on similarities with past operations targeting bulk personally identifiable information.",
                ]},
            ],
            "prepared_by": "Prepared by DHS with reporting from CIA, DHS, FBI, NSA, OSE, State, and open sources.",
        },
    ],
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    if "--sample" in sys.argv:
        sample_path = os.path.join(here, "sample_brief.json")
        with open(sample_path, "w") as f:
            json.dump(SAMPLE, f, indent=2)
        out = os.path.join(here, "sample_pdb.pdf")
        build(SAMPLE, out)
        print(f"Wrote sample brief -> {sample_path}")
        print(f"Wrote sample PDF   -> {out}")
        return

    if len(sys.argv) < 3:
        print("Usage: python render_pdb.py <brief.json> <out.pdf>", file=sys.stderr)
        print("   or: python render_pdb.py --sample", file=sys.stderr)
        sys.exit(2)

    with open(sys.argv[1]) as f:
        brief = json.load(f)
    build(brief, sys.argv[2])
    print(f"Wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
