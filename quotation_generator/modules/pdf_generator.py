"""ReportLab PDF generation for a single quotation, modelled on the reference PDFs."""
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from config import OUTPUT_DIR
from modules.calculations import LineItem, QuotationTotals, TAX_INTER_STATE, to_decimal
from templates.quotation_template import (
    PAGE_SIZE, MARGIN, CONTENT_WIDTH, GRID_STYLE, HEADER_BG,
    STYLE_TITLE, STYLE_NORMAL, STYLE_LABEL,
    STYLE_CELL, STYLE_CELL_BOLD, STYLE_CELL_RIGHT, STYLE_CELL_RIGHT_BOLD,
    STYLE_CELL_CENTER, STYLE_FOOTER_CENTER,
)


def _fmt_amount(value: Decimal) -> str:
    return f"{Decimal(value):,.2f}".replace(",", "")


def _fmt_qty(value: Decimal) -> str:
    value = to_decimal(value)
    if value == value.to_integral_value():
        return str(int(value))
    return f"{value.normalize()}"


def _fmt_rate(value: Decimal) -> str:
    value = to_decimal(value)
    if value == value.to_integral_value():
        return str(int(value))
    return f"{value.normalize()}"


def _p(text: str, style):
    return Paragraph(text if text else "&nbsp;", style)


def _build_header_block(company: dict, quotation: dict) -> Table:
    company_lines = [
        f"<b>{company['company_name']}</b>",
        company["address"],
        f"GSTIN/UIN: {company['gstin']}",
        f"State Name : {company['state_name']}, Code : {company['state_code']}",
        f"CIN: {company['cin']}",
        f"E-Mail : {company['email']}",
    ]
    company_para = Paragraph("<br/>".join(company_lines), STYLE_NORMAL)

    right_rows = [
        [_p("Voucher No.", STYLE_LABEL), _p("Dated", STYLE_LABEL)],
        [_p(f"<b>{quotation['quotation_number']}</b>", STYLE_CELL),
         _p(f"<b>{quotation['quotation_date']:%d.%m.%Y}</b>", STYLE_CELL)],
        [_p("Mode/Terms of Payment", STYLE_LABEL), ""],
        [_p(quotation.get("payment_terms", ""), STYLE_CELL), ""],
        [_p("Buyer's Ref./Order No.", STYLE_LABEL), _p("Other Reference(s)", STYLE_LABEL)],
        [_p(quotation.get("buyer_ref", ""), STYLE_CELL), _p(quotation.get("other_ref", ""), STYLE_CELL)],
        [_p("Despatch through", STYLE_LABEL), _p("Destination", STYLE_LABEL)],
        [_p(quotation.get("despatch_through", ""), STYLE_CELL), _p(quotation.get("destination", ""), STYLE_CELL)],
        [_p("Terms of Delivery", STYLE_LABEL), ""],
        [_p(quotation.get("delivery_terms", ""), STYLE_CELL), ""],
    ]
    right_table = Table(right_rows, colWidths=[CONTENT_WIDTH * 0.36 / 2] * 2)
    right_table.setStyle(TableStyle([
        ("SPAN", (0, 2), (1, 2)), ("SPAN", (0, 3), (1, 3)),
        ("SPAN", (0, 8), (1, 8)), ("SPAN", (0, 9), (1, 9)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    outer = Table(
        [[company_para, right_table]],
        colWidths=[CONTENT_WIDTH * 0.64, CONTENT_WIDTH * 0.36],
    )
    outer.setStyle(TableStyle(GRID_STYLE + [("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return outer


def _customer_block(label: str, customer: dict) -> Table:
    lines = [f"<b>{label}</b>"]
    if customer.get("name"):
        lines.append(f"<b>{customer['name']}</b>")
    if customer.get("organisation"):
        lines.append(f"<b>{customer['organisation']}</b>")
    if customer.get("address"):
        lines.append(customer["address"])
    if customer.get("gstin"):
        lines.append(f"GSTIN/UIN: {customer['gstin']}")
    if customer.get("state_name"):
        lines.append(f"State Name : {customer['state_name']}, Code : {customer.get('state_code', '')}")
    if customer.get("contact_number"):
        lines.append(f"Contact: {customer['contact_number']}")
    if customer.get("email"):
        lines.append(f"Email: {customer['email']}")

    table = Table([[Paragraph("<br/>".join(lines), STYLE_NORMAL)]], colWidths=[CONTENT_WIDTH])
    table.setStyle(TableStyle(GRID_STYLE))
    return table


def _items_table(items: List[LineItem], vehicle_number: str, totals: QuotationTotals, tax_type: str) -> Table:
    col_widths = [w * CONTENT_WIDTH for w in (0.05, 0.34, 0.10, 0.08, 0.09, 0.08, 0.09, 0.06, 0.11)]

    header = [
        _p("Sl<br/>No.", STYLE_CELL_BOLD), _p("Description of Goods and Services", STYLE_CELL_BOLD),
        _p("Vehicle No", STYLE_CELL_BOLD), _p("GST<br/>Rate", STYLE_CELL_BOLD),
        _p("Due on", STYLE_CELL_BOLD), _p("Quantity", STYLE_CELL_BOLD),
        _p("Rate", STYLE_CELL_BOLD), _p("per", STYLE_CELL_BOLD), _p("Amount", STYLE_CELL_BOLD),
    ]
    rows = [header]
    span_commands = []

    for idx, item in enumerate(items, start=1):
        is_labour = to_decimal(item.quantity) == 0
        qty_text = "" if is_labour else _fmt_qty(item.quantity)
        unit_text = "" if is_labour else item.unit
        rate_text = _fmt_amount(item.rate)
        rows.append([
            _p(str(idx), STYLE_CELL_CENTER),
            _p(item.description, STYLE_CELL),
            _p(vehicle_number if idx == 1 else "", STYLE_CELL_CENTER),
            _p(f"{_fmt_rate(item.gst_rate)} %", STYLE_CELL_CENTER),
            _p(item.due_on, STYLE_CELL_CENTER),
            _p(qty_text, STYLE_CELL_CENTER),
            _p(rate_text, STYLE_CELL_RIGHT),
            _p(unit_text, STYLE_CELL_CENTER),
            _p(_fmt_amount(item.amount), STYLE_CELL_RIGHT),
        ])

    if len(items) > 1:
        span_commands.append(("SPAN", (2, 1), (2, len(items))))

    def _summary_row(label, amount, rate_text="", per_text="", label_style=STYLE_CELL, amount_style=STYLE_CELL_RIGHT):
        amount_text = _fmt_amount(amount) if amount is not None else ""
        return [
            _p(label, label_style), "", "", "", "", "",
            _p(rate_text, STYLE_CELL_CENTER), _p(per_text, STYLE_CELL_CENTER),
            _p(amount_text, amount_style),
        ]

    merged_rate_rows = []  # row indices where Rate/per columns should be blank-merged
    summary_start = len(rows)
    rows.append(_summary_row("", totals.subtotal, amount_style=STYLE_CELL_RIGHT_BOLD))
    merged_rate_rows.append(len(rows) - 1)

    half_rate = _fmt_rate(to_decimal(items[0].gst_rate) / 2) if items and tax_type != TAX_INTER_STATE else ""

    if tax_type == TAX_INTER_STATE:
        igst_rate = _fmt_rate(items[0].gst_rate) if items else ""
        rows.append(_summary_row("Output IGST", totals.igst, igst_rate, "%"))
    else:
        rows.append(_summary_row("Output CGST", totals.cgst, half_rate, "%"))
        rows.append(_summary_row("Output SGST", totals.sgst, half_rate, "%"))

    rows.append(_summary_row("Round Off", totals.round_off))
    merged_rate_rows.append(len(rows) - 1)
    rows.append(_summary_row("<b>Total</b>", totals.grand_total, label_style=STYLE_CELL_BOLD, amount_style=STYLE_CELL_RIGHT_BOLD))
    merged_rate_rows.append(len(rows) - 1)
    # Replace the final amount with the rupee-prefixed grand total text.
    rows[-1][-1] = _p(f"<b>Rs. {_fmt_amount(totals.grand_total)}</b>", STYLE_CELL_RIGHT_BOLD)

    table = Table(rows, colWidths=col_widths, repeatRows=1)
    style_commands = GRID_STYLE + span_commands + [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for r in range(summary_start, len(rows)):
        style_commands.append(("SPAN", (0, r), (5, r)))
        if r in merged_rate_rows:
            style_commands.append(("SPAN", (6, r), (7, r)))
    table.setStyle(TableStyle(style_commands))
    return table


def _footer_block(company: dict, quotation: dict, totals: QuotationTotals) -> List:
    words_table = Table(
        [[_p(f"<b>Amount Chargeable (in words)</b><br/>{totals.amount_in_words}", STYLE_CELL),
          _p("E. & O.E", STYLE_CELL_RIGHT)]],
        colWidths=[CONTENT_WIDTH * 0.7, CONTENT_WIDTH * 0.3],
    )
    words_table.setStyle(TableStyle(GRID_STYLE))

    remarks_table = Table(
        [[_p(f"Remarks: {quotation.get('remarks', '')}", STYLE_CELL)]],
        colWidths=[CONTENT_WIDTH],
    )
    remarks_table.setStyle(TableStyle(GRID_STYLE))

    signature_table = Table(
        [
            ["", _p(f"<b>for {company['company_name']}</b>", STYLE_CELL_RIGHT_BOLD)],
            [_p("Prepared by", STYLE_CELL), ""],
            ["", _p("Verified by", STYLE_CELL)],
            ["", _p(company.get("authorised_signatory", "Authorised Signatory"), STYLE_CELL_RIGHT)],
        ],
        colWidths=[CONTENT_WIDTH * 0.5, CONTENT_WIDTH * 0.5],
        rowHeights=[16, 26, 16, 16],
    )
    signature_table.setStyle(TableStyle(GRID_STYLE))

    pan_table = Table(
        [[_p(f"Company's PAN : <b>{company['pan']}</b>", STYLE_CELL)]],
        colWidths=[CONTENT_WIDTH],
    )
    pan_table.setStyle(TableStyle(GRID_STYLE))

    footer_note = Paragraph("This is a Computer Generated Document", STYLE_FOOTER_CENTER)

    return [words_table, remarks_table, signature_table, pan_table, Spacer(1, 6), footer_note]


def generate_quotation_pdf(
    company: dict,
    quotation: dict,
    items: List[LineItem],
    totals: QuotationTotals,
    output_path: Optional[Path] = None,
) -> Path:
    """Render a single quotation PDF and return the output file path."""
    if output_path is None:
        safe_number = quotation["quotation_number"].replace("/", "-")
        output_path = OUTPUT_DIR / f"{safe_number}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"Quotation {quotation['quotation_number']}",
    )

    delivery = quotation.get("delivery") or quotation["customer"]
    vehicle_number = quotation.get("vehicle_number", "")

    elements = [
        Paragraph("QUOTATION", STYLE_TITLE),
        _build_header_block(company, quotation),
        _customer_block("Despatch To", delivery),
        _customer_block("Invoice To", quotation["customer"]),
        _items_table(items, vehicle_number, totals, quotation.get("tax_type", "intra")),
        Spacer(1, 4),
    ]
    elements.extend(_footer_block(company, quotation, totals))

    doc.build(elements)
    return output_path
