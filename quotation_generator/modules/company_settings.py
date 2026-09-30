"""Company settings persistence (JSON) and the Streamlit Company Settings page."""
import json
import shutil
from pathlib import Path

import streamlit as st

from config import ASSETS_DIR, COMPANY_SETTINGS_FILE, DEFAULT_COMPANY_SETTINGS


def load_company_settings() -> dict:
    """Load company settings from the local JSON file, creating defaults if missing."""
    if not COMPANY_SETTINGS_FILE.exists():
        save_company_settings(DEFAULT_COMPANY_SETTINGS)
        return dict(DEFAULT_COMPANY_SETTINGS)

    try:
        with open(COMPANY_SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        merged = dict(DEFAULT_COMPANY_SETTINGS)
        merged.update(settings)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_COMPANY_SETTINGS)


def save_company_settings(settings: dict) -> None:
    """Persist company settings to the local JSON file."""
    COMPANY_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COMPANY_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def _save_logo(uploaded_file) -> str:
    """Save an uploaded logo image under assets/ and return its path."""
    suffix = Path(uploaded_file.name).suffix or ".png"
    dest = ASSETS_DIR / f"company_logo{suffix}"
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)


def render_company_settings_page():
    st.title("Company Settings")
    st.caption("These details are used on every generated quotation PDF.")

    settings = load_company_settings()

    with st.form("company_settings_form"):
        company_name = st.text_input("Company Name", value=settings["company_name"])
        address = st.text_area("Company Address", value=settings["address"], height=80)

        col1, col2 = st.columns(2)
        with col1:
            cin = st.text_input("CIN", value=settings["cin"])
            gstin = st.text_input("GSTIN", value=settings["gstin"])
            pan = st.text_input("PAN", value=settings["pan"])
        with col2:
            email = st.text_input("Email", value=settings["email"])
            state_name = st.text_input("State", value=settings["state_name"])
            state_code = st.text_input("State Code", value=settings["state_code"])

        authorised_signatory = st.text_input(
            "Authorised Signatory (name or designation)",
            value=settings.get("authorised_signatory", "Authorised Signatory"),
        )

        logo_file = st.file_uploader("Company Logo (optional)", type=["png", "jpg", "jpeg"])
        if settings.get("logo_path") and Path(settings["logo_path"]).exists():
            st.image(settings["logo_path"], width=120, caption="Current logo")

        submitted = st.form_submit_button("Save Settings", type="primary")

        if submitted:
            if not company_name.strip():
                st.error("Company Name is required.")
                return
            if not gstin.strip():
                st.error("GSTIN is required.")
                return

            new_settings = {
                "company_name": company_name.strip(),
                "address": address.strip(),
                "cin": cin.strip(),
                "gstin": gstin.strip(),
                "pan": pan.strip(),
                "email": email.strip(),
                "state_name": state_name.strip(),
                "state_code": state_code.strip(),
                "authorised_signatory": authorised_signatory.strip(),
                "logo_path": settings.get("logo_path", ""),
            }

            if logo_file is not None:
                new_settings["logo_path"] = _save_logo(logo_file)

            save_company_settings(new_settings)
            st.success("Company settings saved successfully.")
            st.rerun()
