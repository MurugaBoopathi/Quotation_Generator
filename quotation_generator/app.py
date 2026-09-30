"""Quotation Generator - Streamlit entry point."""
import streamlit as st
from pathlib import Path

from config import APP_TITLE
from modules.company_settings import render_company_settings_page
from modules.database import get_dashboard_stats
from modules.quotation_form import render_create_quotation_page
from modules.quotation_history import render_quotation_history_page

st.set_page_config(page_title=APP_TITLE, page_icon="\U0001F4C4", layout="wide")

# Load custom CSS for modern theme
_assets_dir = Path(__file__).parent / "assets"
if (_assets_dir / "custom.css").exists():
    st.markdown(
        f"<style>{(_assets_dir / 'custom.css').read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

PAGES = [
    "Dashboard",
    "Create Quotation",
    "Bulk Quotation Generator",
    "Quotation History",
    "Company Settings",
]


def render_dashboard():
    st.title("Dashboard")
    stats = get_dashboard_stats()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quotations", stats["total_count"])
    col2.metric("Total Quotation Value", f"₹ {stats['total_value']:,.2f}")
    col3.metric("Quotations This Month", stats["this_month_count"])

    acol1, acol2 = st.columns(2)
    with acol1:
        if st.button("+ Create New Quotation", width="stretch"):
            st.session_state["_nav"] = "Create Quotation"
            st.rerun()
    with acol2:
        if st.button("Generate Bulk Quotations", width="stretch"):
            st.session_state["_nav"] = "Bulk Quotation Generator"
            st.rerun()

    st.subheader("Recent Quotations")
    if not stats["recent"]:
        st.info("No quotations generated yet. Create your first quotation to see it here.")
        return

    for row in stats["recent"]:
        st.write(
            f"**{row['quotation_number']}** — {row['customer_name'] or row['customer_organisation']} "
            f"— ₹ {float(row['grand_total']):,.2f} — {row['quotation_date']}"
        )


def render_placeholder(page_name: str, stage: str):
    st.title(page_name)
    st.info(f"{page_name} is coming in {stage}.")


def _on_nav_change():
    """Callback for sidebar radio navigation — keeps session state in sync."""
    st.session_state["_nav"] = st.session_state["nav_radio"]


def main():
    st.sidebar.title(APP_TITLE)
    st.sidebar.markdown("---")

    # Use on_change callback so the page switches on the first click.
    st.sidebar.radio(
        "Navigation",
        PAGES,
        index=PAGES.index(st.session_state.get("_nav", "Dashboard")),
        key="nav_radio",
        on_change=_on_nav_change,
    )
    page = st.session_state.get("_nav", "Dashboard")

    if page == "Dashboard":
        render_dashboard()
    elif page == "Create Quotation":
        render_create_quotation_page()
    elif page == "Bulk Quotation Generator":
        render_placeholder(page, "Stage 3")
    elif page == "Quotation History":
        render_quotation_history_page()
    elif page == "Company Settings":
        render_company_settings_page()


if __name__ == "__main__":
    main()

