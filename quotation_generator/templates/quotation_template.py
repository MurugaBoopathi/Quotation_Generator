"""Shared ReportLab style constants and paragraph styles for the quotation PDF."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm

PAGE_SIZE = A4
MARGIN = 1.0 * cm
CONTENT_WIDTH = PAGE_SIZE[0] - 2 * MARGIN

BORDER_COLOR = colors.black
HEADER_BG = colors.HexColor("#EFEFEF")
LINE_WIDTH = 0.6

FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

STYLE_TITLE = ParagraphStyle(
    name="Title", fontName=FONT_BOLD, fontSize=14, alignment=1, spaceAfter=6,
)
STYLE_COMPANY_NAME = ParagraphStyle(
    name="CompanyName", fontName=FONT_BOLD, fontSize=10.5, leading=13,
)
STYLE_NORMAL = ParagraphStyle(
    name="Normal", fontName=FONT_NORMAL, fontSize=8.5, leading=11,
)
STYLE_NORMAL_BOLD = ParagraphStyle(
    name="NormalBold", fontName=FONT_BOLD, fontSize=8.5, leading=11,
)
STYLE_LABEL = ParagraphStyle(
    name="Label", fontName=FONT_NORMAL, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#333333"),
)
STYLE_CELL = ParagraphStyle(
    name="Cell", fontName=FONT_NORMAL, fontSize=8.5, leading=10.5,
)
STYLE_CELL_BOLD = ParagraphStyle(
    name="CellBold", fontName=FONT_BOLD, fontSize=8.5, leading=10.5,
)
STYLE_CELL_RIGHT = ParagraphStyle(
    name="CellRight", fontName=FONT_NORMAL, fontSize=8.5, leading=10.5, alignment=2,
)
STYLE_CELL_RIGHT_BOLD = ParagraphStyle(
    name="CellRightBold", fontName=FONT_BOLD, fontSize=8.5, leading=10.5, alignment=2,
)
STYLE_CELL_CENTER = ParagraphStyle(
    name="CellCenter", fontName=FONT_NORMAL, fontSize=8.5, leading=10.5, alignment=1,
)
STYLE_FOOTER_CENTER = ParagraphStyle(
    name="FooterCenter", fontName=FONT_NORMAL, fontSize=7.5, leading=9.5, alignment=1,
    textColor=colors.HexColor("#444444"),
)

GRID_STYLE = [
    ("GRID", (0, 0), (-1, -1), LINE_WIDTH, BORDER_COLOR),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]
