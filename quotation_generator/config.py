"""Central configuration: paths and application-wide defaults."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

COMPANY_SETTINGS_FILE = DATA_DIR / "company_settings.json"
DATABASE_FILE = DATA_DIR / "quotations.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

APP_TITLE = "Quotation Generator"

DEFAULT_COMPANY_SETTINGS = {
    "company_name": "Aayam Sustainable Energy Private Limited",
    "address": (
        "No. 133D, H.P. Bunk Thottam, Jothipuram, Coimbatore North, "
        "Periyanaickenpalayam, Coimbatore - 641047"
    ),
    "cin": "U27101TZ2025PTC036168",
    "gstin": "33ABDCA8409J1ZO",
    "pan": "ABDCA8409J",
    "email": "aayamse@gmail.com",
    "state_name": "Tamil Nadu",
    "state_code": "33",
    "logo_path": "",
    "authorised_signatory": "Authorised Signatory",
}

# Quotation number format, e.g. ASE-Q-{seq:03d}-{fy}
DEFAULT_QUOTATION_PREFIX = "ASE-Q"
DEFAULT_NUMBER_PADDING = 3

DEFAULT_CUSTOMER = {
    "name": "The President",
    "organisation": "Thriuvettanallur Village Panchayat",
    "address": "",
    "gstin": "",
    "state_name": "Tamil Nadu",
    "state_code": "33",
    "contact_number": "",
    "email": "",
}

UNIT_OPTIONS = ["Nos", "Kg", "Litre", "Meter", "Set", "Box", "Hours"]
GST_RATE_OPTIONS = [0, 5, 12, 18, 28]
DEFAULT_GST_RATE = 18
DEFAULT_DUE_ON_DAYS = 10

TAX_TYPE_INTRA_STATE = "Intra-State (CGST + SGST)"
TAX_TYPE_INTER_STATE = "Inter-State (IGST)"
