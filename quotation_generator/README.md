# Quotation Generator

A Python + Streamlit web application for creating GST-compliant quotations, replacing manual PDF editing with a simple web form.

> **Status:** Stage 1 (UI, company settings, quotation entry form), Stage 2 (GST calculation engine + PDF generation) and Stage 4 (quotation history, dashboard, validation, automated tests) are implemented. Stage 3 (bulk Excel generation, multiple-quotation ZIP export) is still a placeholder in the sidebar.

## Features (current)

* Company Settings page — company details persisted to `data/company_settings.json`, editable logo upload.
* Create Quotation page — quotation info, customer/despatch details, vehicle details, dynamic item table, live GST calculation summary.
* Decimal-based GST engine — supports Intra-State (CGST + SGST) and Inter-State (IGST), configurable rounding, amount-in-words conversion.
* PDF generation with ReportLab, modelled on the reference quotation layout (company header, voucher details, despatch/invoice boxes, items table with merged vehicle number column, tax summary, amount in words, signatures, footer).
* Sequential quotation numbering per financial year (e.g. `ASE-Q-001-26-27`), editable by the user.
* Quotation History — every generated quotation is saved to a local SQLite database (`data/quotations.db`); search by number, filter by customer/date, view full details, re-download the PDF, and export the filtered list to Excel.
* Duplicate quotation number protection — regenerating an existing quotation number prompts for explicit confirmation before overwriting the stored record and PDF.
* Dashboard — total quotations, total quotation value, quotations generated this month, and a recent-quotations list, all computed live from the history database.
* Field-level validation — mandatory fields, positive quantity, non-negative rate, valid GST %, at least one line item, quotation number format, duplicate detection.
* Automated unit tests (`tests/`) covering calculations, amount-in-words, quotation numbering, database persistence, validation and PDF generation.

## Planned (Stage 3)

* Manual "Add Another Quotation" flow to build several quotations before generating.
* Bulk quotation generation from an uploaded Excel file (with a downloadable template), row-level validation errors, preview and correction, and a ZIP download of all generated PDFs.

## Prerequisites

* Python 3.11 or later (tested with 3.13)
* Windows, macOS or Linux

## Installation

```powershell
cd quotation_generator
python -m pip install -r requirements.txt
```

## Running the application

```powershell
streamlit run app.py
```

Then open the URL shown in the terminal (typically `http://localhost:8501`).

## Using the application

### Company Settings

Go to **Company Settings** in the sidebar to review/edit the company name, address, CIN, GSTIN, PAN, email, state and authorised signatory, and optionally upload a logo. Click **Save Settings** to persist changes to `data/company_settings.json`.

### Create Quotation

1. Open **Create Quotation**.
2. Review the auto-generated **Quotation Number** and **Financial Year** (both editable).
3. Fill in buyer's reference, payment/delivery terms, despatch and destination details.
4. Enter customer details. Uncheck "Use same address for delivery" to enter a separate despatch address.
5. Enter the vehicle number (shown as a merged column against all items, matching the reference layout).
6. Choose the tax type — **Intra-State (CGST + SGST)** or **Inter-State (IGST)**.
7. Add line items in the table (use the **+** row button to add, the row checkbox + trash icon to delete). Amount, GST and totals update immediately.
8. Click **Generate PDF** to validate the form and create the PDF in `output/`, then use **Download PDF**. The quotation is also saved to the local history database.
9. Use **Clear Form** to reset all fields for a new quotation.
10. If you re-generate a quotation number that already exists in history, you'll be asked to confirm before it overwrites the existing record and PDF.

### Dashboard

Shows total quotations generated, total quotation value, quotations generated this month, and the 5 most recent quotations — all computed from the history database. Quick-action buttons jump straight to Create Quotation or Bulk Quotation Generator.

### Quotation History

Search by quotation number, filter by customer name and/or date range, view full details (subtotal, GST breakdown, grand total) for any quotation, re-download its PDF, and export the current filtered list to Excel.

## Project structure

```
quotation_generator/
  app.py                     # Streamlit entry point / sidebar navigation
  config.py                  # Paths and application defaults
  requirements.txt
  modules/
    company_settings.py      # Company settings persistence + page
    quotation_form.py        # Create Quotation page
    quotation_history.py     # Quotation History page
    database.py              # SQLite persistence (quotation history, dashboard stats)
    calculations.py          # Decimal GST calculation engine
    pdf_generator.py         # ReportLab PDF generation
    number_to_words.py       # Indian-currency amount-in-words conversion
    validators.py            # Form validation + duplicate quotation number check
  templates/
    quotation_template.py    # Shared ReportLab styles/constants
  tests/                     # Automated unit tests (unittest)
  data/
    company_settings.json    # Persisted company settings
    quotations.db            # SQLite quotation history (created on first run)
  output/                    # Generated PDFs
  assets/                    # Uploaded logo, etc.
```

## Calculation reference

The calculation engine (`modules/calculations.py`) is verified against the two sample quotations:

| | Sample 1 | Sample 2 |
|---|---|---|
| Items | 600, 1500, 360, 1000 | 600, 1000, 300 |
| Subtotal | 3,460.00 | 1,900.00 |
| CGST @ 9% | 311.40 | 171.00 |
| SGST @ 9% | 311.40 | 171.00 |
| Round Off | 0.20 | 0.00 |
| Grand Total | 4,083.00 | 2,242.00 |

## Running the tests

```powershell
cd quotation_generator
python -m unittest discover -s tests -t . -v
```

The suite covers item/CGST/SGST/IGST/round-off calculations (including both sample quotations above), amount-in-words conversion, sequential quotation numbering, SQLite history persistence and duplicate detection, form validation, and PDF generation.

## Troubleshooting

* **`ModuleNotFoundError`** — re-run `python -m pip install -r requirements.txt` in the same Python environment used to start Streamlit.
* **Rupee symbol not visible in PDF** — ReportLab's built-in Helvetica font does not support the ₹ glyph, so PDFs use `Rs.` as the currency prefix. The Streamlit UI itself displays ₹ normally (browser font).
* **Port already in use** — run `streamlit run app.py --server.port 8502` (or any free port).
* **Company settings not saving** — ensure the `data/` folder is writable; the app creates it automatically on first run.
* **"Quotation number already exists" warning** — this is expected duplicate protection; confirm the overwrite or change the quotation number.
