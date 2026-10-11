"""Render the resume PDF from resume.json + stats/stats.json (deterministic output)."""
import os
import sys
import json

os.environ.setdefault("RL_invariant", "1")  # byte-identical output when content is unchanged

from reportlab import rl_config
rl_config.invariant = 1
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth, registerFontFamily
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "Wycliffe_Kipleting_Rotich_Resume_Public.pdf")
DATA = json.load(open(os.path.join(ROOT, "resume.json")))
STATS = json.load(open(os.path.join(ROOT, "stats", "stats.json")))


def fill(text):
    for k, v in STATS.items():
        text = text.replace("{{%s}}" % k, str(v))
    return text


FD = os.path.join(ROOT, "build", "fonts")
for name, f in [("Plex", "Regular"), ("Plex-Medium", "Medium"), ("Plex-Semi", "SemiBold"),
                ("Plex-Bold", "Bold"), ("Plex-Italic", "Italic")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FD, "IBMPlexSans-%s.ttf" % f)))
registerFontFamily("Plex", normal="Plex", bold="Plex-Semi", italic="Plex-Italic", boldItalic="Plex-Semi")

INK = HexColor("#0A1020"); AMBER = HexColor("#F5A524"); TEXT = HexColor("#1F2937")
MUTED = HexColor("#5B6678"); LIGHT = HexColor("#F3F5F9"); RULE = HexColor("#D9DEE8"); TEAL = HexColor("#0E9F8E")

W, H = A4
LM = RM = 40
CW = W - LM - RM
BAND = 112

body = ParagraphStyle("body", fontName="Plex", fontSize=8.7, leading=12.1, textColor=TEXT)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=11, bulletIndent=0, spaceAfter=2.6,
                        bulletFontName="Plex-Bold", bulletFontSize=8.7, bulletColor=AMBER)
role = ParagraphStyle("role", fontName="Plex-Bold", fontSize=10, leading=13, textColor=INK)
dates = ParagraphStyle("dates", fontName="Plex-Medium", fontSize=8.4, leading=13, textColor=MUTED, alignment=TA_RIGHT)
company = ParagraphStyle("company", fontName="Plex-Medium", fontSize=8.8, leading=11.5, textColor=TEAL)
sec = ParagraphStyle("sec", fontName="Plex-Bold", fontSize=9, leading=11, textColor=INK)
skl = ParagraphStyle("skl", fontName="Plex-Semi", fontSize=8.4, leading=11.6, textColor=INK)
skv = ParagraphStyle("skv", parent=body, fontSize=8.4, leading=11.6)


def section(title):
    t = Table([[Paragraph(title.upper(), sec)]], colWidths=[CW])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.6, RULE), ("LINEBEFORE", (0, 0), (0, -1), 3, AMBER),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return [Spacer(1, 7), t, Spacer(1, 5)]


def job_head(title, dt, org):
    t = Table([[Paragraph(title, role), Paragraph(dt, dates)]], colWidths=[CW - 120, 120])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                           ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    return [t, Paragraph(org, company), Spacer(1, 3.5)]


def bl(text):
    return Paragraph(fill(text), bullet, bulletText="\u2022")


def first_page(c, doc):
    c.saveState()
    c.setFillColor(INK); c.rect(0, H - BAND, W, BAND, stroke=0, fill=1)
    c.setFillColor(AMBER); c.rect(0, H - BAND - 3, W, 3, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Plex-Bold", 25); c.drawString(LM, H - 50, DATA["name"])
    c.setFillColor(AMBER); c.setFont("Plex-Medium", 10.5); c.drawString(LM, H - 68, DATA["headline"])
    c.setFillColor(HexColor("#CBD5E1")); c.setFont("Plex-Medium", 8.4)
    for i, line in enumerate(DATA["availability"]):
        c.drawRightString(W - RM, H - 50 - 12 * i, line)

    def row(y, items):
        x = LM
        c.setFont("Plex", 8.4)
        for i, (label, url) in enumerate(items):
            c.setFillColor(HexColor("#E2E8F0")); c.drawString(x, y, label)
            wl = stringWidth(label, "Plex", 8.4)
            if url:
                c.linkURL(url, (x, y - 2, x + wl, y + 9), relative=0)
            x += wl
            if i < len(items) - 1:
                c.setFillColor(AMBER); c.drawString(x + 6, y, "|"); x += 18
    for i, items in enumerate(DATA["contact_rows"]):
        row(H - 88 - 13 * i, items)
    c.restoreState()


def later_page(c, doc):
    c.saveState()
    c.setFillColor(AMBER); c.rect(0, H - 6, W, 6, stroke=0, fill=1)
    c.setFont("Plex-Medium", 7.5); c.setFillColor(MUTED)
    c.drawString(LM, 24, "%s  |  Platform Engineer  |  Nairobi, Kenya" % DATA["name"])
    c.drawRightString(W - RM, 24, "Page %d" % doc.page)
    c.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, title="%s - Resume" % DATA["name"], author=DATA["name"],
                      subject="Platform Engineer resume", leftMargin=LM, rightMargin=RM)
f1 = Frame(LM, 36, CW, H - BAND - 3 - 36 - 14, id="f1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
f2 = Frame(LM, 40, CW, H - 40 - 30, id="f2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="First", frames=[f1], onPage=first_page, autoNextPageTemplate="Later"),
                      PageTemplate(id="Later", frames=[f2], onPage=later_page)])

S = []
# metrics strip
cells = []
for m in DATA["metrics"]:
    cells.append([Paragraph('<font name="Plex-Bold" size="15" color="#0A1020">%s</font>' % fill(m["value"]),
                            ParagraphStyle("m", leading=17)),
                  Paragraph('<font name="Plex" size="7.4" color="#5B6678">%s</font>' % m["label"],
                            ParagraphStyle("ml", leading=9))])
mt = Table([cells], colWidths=[CW * 0.2, CW * 0.2, CW * 0.2, CW * 0.4])
mt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEABOVE", (0, 0), (-1, 0), 1.5, AMBER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LINEAFTER", (0, 0), (-2, -1), 0.5, RULE)]))
S += [mt]

S += section("Professional summary")
S.append(Paragraph(fill(DATA["summary"]), body))

S += section("Technical skills")
st = Table([[Paragraph(a, skl), Paragraph(b, skv)] for a, b in DATA["skills"]], colWidths=[95, CW - 95])
st.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1.6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6), ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE)]))
S.append(st)

S += section("Professional experience")
for i, j in enumerate(DATA["experience"]):
    head = job_head(j["title"], j["dates"], j["org"])
    bullets = [bl(b) for b in j["bullets"]]
    if i == 0:                                  # long entry: let it flow across the page break
        S += head + bullets
    else:
        S.append(KeepTogether(head + bullets))
    S.append(Spacer(1, 5 if i == 0 else 4))

S += section("Education")
for e in DATA["education"]:
    S += job_head(e["title"], e["dates"], e["school"])
    S.append(Spacer(1, 2))

doc.build(S)
print("PDF written:", OUT)
