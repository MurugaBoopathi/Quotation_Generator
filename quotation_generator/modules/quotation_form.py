"""Create Quotation page: quotation info, customer, vehicle and dynamic item entry."""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st

from config import (
    DATA_DIR, DEFAULT_CUSTOMER, DEFAULT_DUE_ON_DAYS, DEFAULT_GST_RATE,
    DEFAULT_NUMBER_PADDING, DEFAULT_QUOTATION_PREFIX, GST_RATE_OPTIONS,
    TAX_TYPE_INTER_STATE, TAX_TYPE_INTRA_STATE, UNIT_OPTIONS,
)
from modules.calculations import LineItem, QuotationTotals, TAX_INTER_STATE, TAX_INTRA_STATE, calculate_totals, to_decimal
from modules.company_settings import load_company_settings
from modules.database import quotation_exists, save_quotation
from modules.pdf_generator import generate_quotation_pdf
from modules.validators import validate_quotation

QUOTATION_SEQ_FILE = DATA_DIR / "quotation_seq.json"

EMPTY_ITEM_ROW = {
    "Description": "",
    "Type": "Regular",
    "Quantity": 1.0,
    "Unit": "Nos",
    "Rate": 0.0,
}


def financial_year_for(d: date) -> str:
    """Return the Indian financial year string (e.g. '25-26') for a given date."""
    if d.month >= 4:
        start, end = d.year, d.year + 1
    else:
        start, end = d.year - 1, d.year
    return f"{start % 100:02d}-{end % 100:02d}"


def _load_seq_map() -> dict:
    if QUOTATION_SEQ_FILE.exists():
        try:
            return json.loads(QUOTATION_SEQ_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_seq_map(seq_map: dict) -> None:
    QUOTATION_SEQ_FILE.write_text(json.dumps(seq_map, indent=2), encoding="utf-8")


def peek_next_quotation_number(prefix: str, fy: str) -> str:
    """Return the next quotation number for the given financial year without consuming it."""
    seq_map = _load_seq_map()
    next_seq = seq_map.get(fy, 0) + 1
    return f"{prefix}-{next_seq:0{DEFAULT_NUMBER_PADDING}d}-{fy}"


def commit_quotation_number(prefix: str, fy: str) -> None:
    """Advance the stored sequence counter for the given financial year."""
    seq_map = _load_seq_map()
    seq_map[fy] = seq_map.get(fy, 0) + 1
    _save_seq_map(seq_map)


def _init_session_state():
    st.session_state.setdefault("_items_base", pd.DataFrame([EMPTY_ITEM_ROW]))
    st.session_state.setdefault("quotation_date", date.today())
    fy_default = financial_year_for(st.session_state["quotation_date"])
    st.session_state.setdefault("financial_year", fy_default)
    st.session_state.setdefault(
        "quotation_number",
        peek_next_quotation_number(DEFAULT_QUOTATION_PREFIX, fy_default),
    )
    st.session_state.setdefault("customer", dict(DEFAULT_CUSTOMER))
    st.session_state.setdefault("same_as_customer", True)
    st.session_state.setdefault("delivery", dict(DEFAULT_CUSTOMER))


def _clear_form():
    for key in ("_items_base", "items_editor", "quotation_date", "financial_year", "quotation_number", "customer", "delivery", "same_as_customer", "common_gst_rate", "common_due_on"):
        st.session_state.pop(key, None)
    st.session_state.pop("last_generated_pdf", None)
    st.session_state.pop("pending_duplicate", None)


def _build_history_record(quotation: dict, totals: QuotationTotals, pdf_path: Path) -> dict:
    customer = quotation["customer"]
    return {
        "quotation_number": quotation["quotation_number"],
        "quotation_date": quotation["quotation_date"].isoformat(),
        "financial_year": quotation.get("financial_year", ""),
        "customer_name": customer.get("name", ""),
        "customer_organisation": customer.get("organisation", ""),
        "vehicle_number": quotation.get("vehicle_number", ""),
        "tax_type": quotation.get("tax_type", ""),
        "subtotal": totals.subtotal,
        "cgst": totals.cgst,
        "sgst": totals.sgst,
        "igst": totals.igst,
        "round_off": totals.round_off,
        "grand_total": totals.grand_total,
        "pdf_path": str(pdf_path),
    }


def _dataframe_to_items(df: pd.DataFrame, common_gst_rate, common_due_on: str) -> list:
    """Convert the editor DataFrame to LineItem objects.

    Uses the common GST rate and Due On values. For labour-type rows
    (Type == 'Labour'), quantity is set to 0 so that amount = rate directly.
    """
    items = []
    for idx, row in df.iterrows():
        raw_type = row.get("Type", "Regular")
        item_type = str(raw_type).strip() if raw_type is not None and str(raw_type).strip().lower() != "nan" else "Regular"
        is_labour = item_type.lower() == "labour"
        qty_raw = row.get("Quantity", 0)
        # Labour items: quantity is irrelevant — set to 0 so amount = rate.
        quantity = Decimal("0") if is_labour else to_decimal(qty_raw)
        raw_unit = row.get("Unit", "Nos")
        unit = "" if is_labour else (str(raw_unit).strip() or "Nos" if raw_unit is not None and str(raw_unit).strip().lower() != "nan" else "Nos")
        items.append(
            LineItem(
                sl_no=int(idx) + 1,
                description=str(row.get("Description", "")).strip(),
                gst_rate=to_decimal(common_gst_rate),
                due_on=common_due_on.strip(),
                quantity=quantity,
                unit=unit,
                rate=to_decimal(row.get("Rate", 0)),
            )
        )
    return items


def render_create_quotation_page():
    st.title("Create Quotation")
    _init_session_state()
    company = load_company_settings()

    with st.expander("Quotation Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            quotation_date = st.date_input("Quotation Date", value=st.session_state["quotation_date"])
            st.session_state["quotation_date"] = quotation_date
        with col2:
            financial_year = st.text_input("Financial Year", value=st.session_state["financial_year"])
            st.session_state["financial_year"] = financial_year
        with col3:
            quotation_number = st.text_input("Quotation Number", value=st.session_state["quotation_number"])
            st.session_state["quotation_number"] = quotation_number

        col4, col5 = st.columns(2)
        with col4:
            buyer_ref = st.text_input("Buyer's Reference / Order No.", value=st.session_state["quotation_number"], key="buyer_ref")
            payment_terms = st.text_input("Mode / Terms of Payment", key="payment_terms")
            despatch_through = st.text_input("Despatch Through", key="despatch_through")
            due_on_default = st.text_input("Due on / Delivery Period", value=f"{DEFAULT_DUE_ON_DAYS} Days", key="due_on_default")
        with col5:
            other_ref = st.text_input("Other Reference(s)", key="other_ref")
            delivery_terms = st.text_input("Terms of Delivery", key="delivery_terms")
            destination = st.text_input("Destination", key="destination")

        remarks = st.text_area("Remarks", key="remarks", height=70)

    with st.expander("Customer Details", expanded=True):
        customer = st.session_state["customer"]
        col1, col2 = st.columns(2)
        with col1:
            customer["name"] = st.text_input("Customer / Buyer Name", value=customer["name"], key="cust_name")
            customer["organisation"] = st.text_input("Organisation", value=customer["organisation"], key="cust_org")
            customer["address"] = st.text_area("Customer Address", value=customer["address"], key="cust_address", height=70)
            customer["gstin"] = st.text_input("GSTIN / UIN", value=customer["gstin"], key="cust_gstin")
        with col2:
            customer["state_name"] = st.text_input("State Name", value=customer["state_name"], key="cust_state")
            customer["state_code"] = st.text_input("State Code", value=customer["state_code"], key="cust_state_code")
            customer["contact_number"] = st.text_input("Contact Number (optional)", value=customer["contact_number"], key="cust_contact")
            customer["email"] = st.text_input("Email (optional)", value=customer["email"], key="cust_email")

        same_as_customer = st.checkbox("Use same address for delivery (Despatch To)", value=st.session_state["same_as_customer"])
        st.session_state["same_as_customer"] = same_as_customer

        if not same_as_customer:
            st.markdown("**Delivery Address**")
            delivery = st.session_state["delivery"]
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                delivery["name"] = st.text_input("Delivery Name", value=delivery["name"], key="deliv_name")
                delivery["organisation"] = st.text_input("Delivery Organisation", value=delivery["organisation"], key="deliv_org")
                delivery["address"] = st.text_area("Delivery Address", value=delivery["address"], key="deliv_address", height=70)
            with dcol2:
                delivery["state_name"] = st.text_input("Delivery State", value=delivery["state_name"], key="deliv_state")
                delivery["state_code"] = st.text_input("Delivery State Code", value=delivery["state_code"], key="deliv_state_code")

    with st.expander("Vehicle Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            vehicle_number = st.text_input("Vehicle Number", key="vehicle_number")
        with col2:
            vehicle_description = st.text_input("Vehicle Description (optional)", key="vehicle_description")

    with st.expander("Tax Configuration", expanded=True):
        tax_type_label = st.radio("Tax Type", [TAX_TYPE_INTRA_STATE, TAX_TYPE_INTER_STATE], horizontal=True)
        tax_type = TAX_INTRA_STATE if tax_type_label == TAX_TYPE_INTRA_STATE else TAX_INTER_STATE

    st.subheader("Item Details")

    # Common GST Rate and Due On — apply to all rows.
    st.session_state.setdefault("common_gst_rate", DEFAULT_GST_RATE)
    st.session_state.setdefault("common_due_on", f"{DEFAULT_DUE_ON_DAYS} Days")

    common_col1, common_col2 = st.columns(2)
    with common_col1:
        common_gst_rate = st.selectbox(
            "Common GST Rate (%) — applies to all items",
            options=GST_RATE_OPTIONS,
            index=GST_RATE_OPTIONS.index(st.session_state["common_gst_rate"])
            if st.session_state["common_gst_rate"] in GST_RATE_OPTIONS else 0,
            key="common_gst_select",
        )
        st.session_state["common_gst_rate"] = common_gst_rate
    with common_col2:
        common_due_on = st.text_input(
            "Common Due On — applies to all items",
            value=st.session_state["common_due_on"],
            key="common_due_on_input",
        )
        st.session_state["common_due_on"] = common_due_on

    st.caption("Use the + button at the bottom of the table to add a row, and the row checkbox + delete icon to remove one. Set Type to 'Labour' for items where only an amount is needed (e.g. Labour Charges).")

    # _items_base is the stable data source — it only changes on Clear Form.
    # The data_editor widget manages its own edit state internally via key.
    # We must NOT write the return value back to _items_base, because doing so
    # changes the input data on the next rerun and causes the widget to reset,
    # making entered values disappear.
    edited_df = st.data_editor(
        st.session_state["_items_base"],
        num_rows="dynamic",
        width="stretch",
        key="items_editor",
        column_config={
            "Description": st.column_config.TextColumn("Description of Goods and Services", required=True, width="large"),
            "Type": st.column_config.SelectboxColumn("Type", options=["Regular", "Labour"], required=True),
            "Quantity": st.column_config.NumberColumn("Quantity", min_value=0.0, step=1.0, format="%.2f"),
            "Unit": st.column_config.SelectboxColumn("Unit", options=UNIT_OPTIONS),
            "Rate": st.column_config.NumberColumn("Rate (Amount for Labour)", min_value=0.0, step=1.0, format="%.2f"),
        },
    )

    items = _dataframe_to_items(edited_df, common_gst_rate, common_due_on)
    totals = calculate_totals(items, tax_type=tax_type)

    st.subheader("Calculation Summary")
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Subtotal", f"₹ {totals.subtotal:,.2f}")
    if tax_type == TAX_INTER_STATE:
        scol2.metric("IGST", f"₹ {totals.igst:,.2f}")
    else:
        scol2.metric("CGST", f"₹ {totals.cgst:,.2f}")
        scol3.metric("SGST", f"₹ {totals.sgst:,.2f}")
    st.write(f"Round Off: ₹ {totals.round_off:,.2f}")
    st.success(f"Grand Total: ₹ {totals.grand_total:,.2f}")
    st.caption(f"Amount in words: {totals.amount_in_words}")

    quotation = {
        "quotation_number": st.session_state["quotation_number"],
        "quotation_date": quotation_date,
        "financial_year": financial_year,
        "buyer_ref": buyer_ref,
        "other_ref": other_ref,
        "payment_terms": payment_terms,
        "delivery_terms": delivery_terms,
        "despatch_through": despatch_through,
        "destination": destination,
        "remarks": remarks,
        "customer": customer,
        "delivery": None if same_as_customer else st.session_state["delivery"],
        "vehicle_number": vehicle_number,
        "vehicle_description": vehicle_description,
        "tax_type": tax_type,
        "items": edited_df.rename(columns={
            "Description": "description", "Type": "type",
            "Quantity": "quantity", "Unit": "unit", "Rate": "rate",
        }).assign(
            gst_rate=common_gst_rate,
            due_on=common_due_on,
        ).to_dict("records"),
    }

    def _do_generate(overwrite: bool):
        output_path = generate_quotation_pdf(company, quotation, items, totals)
        commit_quotation_number(DEFAULT_QUOTATION_PREFIX, financial_year)
        save_quotation(_build_history_record(quotation, totals, output_path), overwrite=overwrite)
        st.session_state["last_generated_pdf"] = str(output_path)
        st.session_state.pop("pending_duplicate", None)
        st.success(f"Quotation PDF generated: {output_path.name}")

    st.divider()
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        generate_clicked = st.button("Generate PDF", type="primary", width="stretch")
    with bcol2:
        clear_clicked = st.button("Clear Form", width="stretch")

    if clear_clicked:
        _clear_form()
        st.rerun()

    if generate_clicked:
        errors = validate_quotation(quotation)
        if errors:
            st.session_state.pop("pending_duplicate", None)
            for err in errors:
                st.error(err)
        elif quotation_exists(quotation["quotation_number"]):
            st.session_state["pending_duplicate"] = quotation["quotation_number"]
        else:
            _do_generate(overwrite=False)

    if st.session_state.get("pending_duplicate") == quotation["quotation_number"]:
        st.warning(
            f"Quotation number '{quotation['quotation_number']}' already exists in "
            "Quotation History. Generating again will overwrite the stored record and PDF."
        )
        wcol1, wcol2 = st.columns(2)
        with wcol1:
            if st.button("Yes, overwrite and generate", type="primary", width="stretch"):
                _do_generate(overwrite=True)
        with wcol2:
            if st.button("Cancel", width="stretch"):
                st.session_state.pop("pending_duplicate", None)
                st.rerun()

    if st.session_state.get("last_generated_pdf"):
        pdf_path = Path(st.session_state["last_generated_pdf"])
        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    data=f.read(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    width="stretch",
                )
