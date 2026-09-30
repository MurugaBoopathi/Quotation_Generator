"""Quotation History page: search, filter, view details, download PDFs, export to Excel."""
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.database import list_quotations

DISPLAY_COLUMNS = {
    "quotation_number": "Quotation Number",
    "quotation_date": "Quotation Date",
    "customer_name": "Customer Name",
    "vehicle_number": "Vehicle Number",
    "subtotal": "Subtotal",
    "gst": "GST",
    "grand_total": "Grand Total",
    "generated_at": "Generation Date",
}


def _to_display_dataframe(rows: list) -> pd.DataFrame:
    records = []
    for row in rows:
        gst = Decimal(row["cgst"]) + Decimal(row["sgst"]) + Decimal(row["igst"])
        records.append({
            "quotation_number": row["quotation_number"],
            "quotation_date": row["quotation_date"],
            "customer_name": row["customer_name"] or row["customer_organisation"],
            "vehicle_number": row["vehicle_number"],
            "subtotal": float(row["subtotal"]),
            "gst": float(gst),
            "grand_total": float(row["grand_total"]),
            "generated_at": row["generated_at"],
        })
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.rename(columns=DISPLAY_COLUMNS)
    return df


def render_quotation_history_page():
    st.title("Quotation History")

    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    with fcol1:
        search_number = st.text_input("Search by Quotation Number")
    with fcol2:
        customer_filter = st.text_input("Filter by Customer Name")
    with fcol3:
        date_from = st.date_input("From Date", value=None)
    with fcol4:
        date_to = st.date_input("To Date", value=None)

    rows = list_quotations(
        search_number=search_number,
        customer_name=customer_filter,
        date_from=date_from if isinstance(date_from, date) else None,
        date_to=date_to if isinstance(date_to, date) else None,
    )

    if not rows:
        st.info("No quotations found. Generate a quotation from Create Quotation to see it here.")
        return

    df = _to_display_dataframe(rows)
    st.dataframe(
        df,
        width="stretch",
        column_config={
            "Subtotal": st.column_config.NumberColumn(format="₹ %.2f"),
            "GST": st.column_config.NumberColumn(format="₹ %.2f"),
            "Grand Total": st.column_config.NumberColumn(format="₹ %.2f"),
        },
    )

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, sheet_name="Quotation History")
    st.download_button(
        "Export to Excel",
        data=excel_buffer.getvalue(),
        file_name="quotation_history.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("View Quotation Details")
    quotation_numbers = [row["quotation_number"] for row in rows]
    selected = st.selectbox("Select a quotation to view/download", quotation_numbers)
    selected_row = next(row for row in rows if row["quotation_number"] == selected)

    with st.expander(f"Details for {selected}", expanded=True):
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.write(f"**Quotation Date:** {selected_row['quotation_date']}")
            st.write(f"**Customer:** {selected_row['customer_name']}")
            st.write(f"**Organisation:** {selected_row['customer_organisation']}")
            st.write(f"**Vehicle Number:** {selected_row['vehicle_number']}")
            st.write(f"**Tax Type:** {selected_row['tax_type']}")
        with dcol2:
            st.write(f"**Subtotal:** ₹ {Decimal(selected_row['subtotal']):,.2f}")
            st.write(f"**CGST:** ₹ {Decimal(selected_row['cgst']):,.2f}")
            st.write(f"**SGST:** ₹ {Decimal(selected_row['sgst']):,.2f}")
            st.write(f"**IGST:** ₹ {Decimal(selected_row['igst']):,.2f}")
            st.write(f"**Round Off:** ₹ {Decimal(selected_row['round_off']):,.2f}")
            st.write(f"**Grand Total:** ₹ {Decimal(selected_row['grand_total']):,.2f}")

        pdf_path = Path(selected_row["pdf_path"]) if selected_row["pdf_path"] else None
        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    data=f.read(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    key=f"download_{selected}",
                )
        else:
            st.caption("The original PDF file is no longer available on disk.")
