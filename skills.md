# Project: Python Streamlit Quotation Generator

Act as a senior Python developer and build a complete, production-ready quotation generation web application using **Python and Streamlit**.

I have attached two sample quotation PDFs. Use these PDFs as the primary reference for the quotation layout, formatting, company information, fields and overall appearance.

The objective is to eliminate manual PDF editing. Users should be able to enter quotation details through a web interface, automatically calculate amounts and generate downloadable PDFs. The application must also support generating multiple quotations with different amounts.

## 1. Technology stack

Use the following technologies:

* Python 3.11 or later
* Streamlit for the web UI
* ReportLab for PDF generation
* Pandas for tabular data and bulk quotation processing
* OpenPyXL for Excel import and export
* Pillow, if required for logos and images
* Python standard libraries for date, decimal calculations, ZIP files and number-to-words conversion

Use a modular architecture with separate files for the UI, calculations, PDF generation, configuration and data management.

## 2. Application UI

Create a clean, modern and user-friendly Streamlit application.

Application title: **Quotation Generator**

Use a sidebar with the following navigation options:

1. Dashboard
2. Create Quotation
3. Bulk Quotation Generator
4. Quotation History
5. Company Settings

The interface should be responsive, easy to use and suitable for non-technical users.

Use clear labels, helpful validation messages, appropriate buttons, tables and success notifications.

## 3. Company details

Create a Company Settings page where the user can configure and save the following details:

* Company Name: Aayam Sustainable Energy Private Limited
* Company Address: No. 133D, H.P. Bunk Thottam, Jothipuram, Coimbatore North, Periyanaickenpalayam, Coimbatore - 641047
* CIN: U27101TZ2025PTC036168
* GSTIN: 33ABDCA8409J1ZO
* PAN: ABDCA8409J
* Email: [aayamse@gmail.com](mailto:aayamse@gmail.com)
* State: Tamil Nadu
* State Code: 33
* Company Logo: Optional image upload
* Authorised Signatory: Configurable name or designation

The company information should be pre-populated but editable through the settings page.

Persist the configuration in a local JSON file so that it is retained when the application restarts.

Do not hardcode company details throughout the PDF generation logic. Read them from the configuration.

## 4. Create Quotation page

Create a form to enter the following information.

### A. Quotation information

* Quotation Number: Automatically generate a sequential quotation number, with an option to edit it.
* Financial Year: Allow configuration, with a suitable default based on the quotation date.
* Quotation Date: Default to the current date, but editable.
* Buyer's Reference / Order Number
* Other References
* Mode / Terms of Payment
* Terms of Delivery
* Despatch Through
* Destination
* Due on / Delivery Period: Default to 10 days, editable.
* Remarks

Use a configurable quotation number format such as ASE-Q-001-26-27. Allow the user to change the prefix and format.

### B. Customer details

Provide input fields for:

* Customer / Buyer Name
* Customer Address
* GSTIN / UIN
* State Name
* State Code
* Contact Number (optional)
* Email (optional)

Add a checkbox to use the same customer for the delivery address.

If unchecked, display separate delivery address fields.

Pre-populate the following customer information from the sample PDFs:

Customer Name: The President
Organisation: Thriuvettanallur Village Panchayat

Allow the user to edit all customer details.

### C. Vehicle details

Provide the following fields:

* Vehicle Number
* Vehicle Description (optional)

### D. Item details

Create a dynamic line-item table where the user can add, edit and remove items.

Each item should have the following fields:

* Sl. No.
* Description of Goods and Services
* GST Rate (%)
* Due On
* Quantity
* Unit (Nos, Kg, Litre, etc.)
* Rate
* Amount

The line-item table must allow users to add any number of items.

Provide an Add Item button and a Delete button for each item.

The Amount for each line item should be automatically calculated as:

Amount = Quantity × Rate

Allow the user to edit quantities, descriptions, units, rates and GST percentages.

Use Decimal arithmetic rather than floating-point arithmetic for all financial calculations.

### E. GST and total calculations

Implement automatic GST calculations.

The application should support:

* CGST
* SGST
* IGST
* Round Off
* Grand Total

For the sample quotations, the default GST rate is 18%, split into CGST 9% and SGST 9%.

The tax calculation must be configurable for each item.

Support the following tax scenarios:

1. Intra-state transactions: CGST + SGST
2. Inter-state transactions: IGST

Provide an option to select the tax type, with intra-state selected by default.

Calculate the taxable subtotal by summing the item amounts.

Calculate GST using the configured tax rates and display each tax component separately.

Round the final payable amount to the nearest whole rupee by default. Allow the rounding mode to be configured.

Show the following summary:

* Subtotal
* Output CGST
* Output SGST
* Output IGST, if applicable
* Round Off
* Grand Total

Use the following formulas:

Subtotal = Sum of all item amounts

Taxable Amount = Sum of the applicable item amounts

Grand Total = Subtotal + Applicable Taxes + Round Off

Ensure that the calculation is consistent with the selected tax configuration.

Also generate the total amount in words in Indian currency format, for example, Rupees Four Thousand Eighty-Three Only.

Make sure all calculations are updated immediately whenever the user changes an item or rate.

## 5. PDF generation

Use ReportLab to generate a professional PDF closely matching the attached quotation PDFs.

The PDF should have:

* A4 page size
* Portrait orientation
* Proper margins
* Clear typography
* Consistent spacing
* Proper alignment of numerical values
* Professional table borders
* Bold headings and totals
* Rupee currency formatting

Follow the layout and terminology of the reference PDFs as closely as practical.

### PDF layout

**Header**

Display:

* Company name
* Company address
* CIN
* GSTIN
* PAN
* Email
* QUOTATION title

**Quotation details**

Display:

* Quotation number
* Date
* Buyer's reference
* Other references
* Payment terms
* Delivery terms
* Despatch information
* Destination

**Customer and delivery information**

Display:

* Invoice To / Customer details
* Despatch To / Delivery details
* Vehicle number

**Items table**

Use these columns:

| Sl. No. | GST Rate | Due On | Quantity | Rate | Per | Amount |
| Description of Goods and Services | | | | | | |

Use a layout that accommodates long item descriptions and multiple line items. The description should be displayed clearly without overlapping other columns.

**Amount summary**

Display:

* Subtotal
* Output CGST
* Output SGST
* Output IGST, when applicable
* Round Off
* Total

Highlight the final payable amount.

**Footer**

Display:

* Amount Chargeable (in words)
* Remarks
* E. & O.E.
* Prepared by
* Verified by Authorised Signatory
* Company name and signature area
* "This is a Computer Generated Document"

Ensure the PDF is readable, with no overlapping text, missing fields, clipped tables or broken alignment.

When there are many items, allow the table to continue onto additional pages. Repeat the table header on each page and keep the totals and footer together wherever possible.

## 6. Multiple quotation generation

This is one of the most important features.

Provide two ways to generate quotations:

### Option A: Generate multiple quotations manually

Allow the user to create multiple quotations for the same customer or different customers.

Provide a button called "Add Another Quotation".

Each quotation should have its own:

* Quotation number
* Date
* Customer information
* Vehicle details
* Items
* Rates
* GST calculations
* Grand total

Allow users to review all quotations before generating the PDFs.

Provide the following actions:

* Generate PDF
* Generate All PDFs
* Download All as ZIP
* Clear Form

Each PDF should be generated separately, with a unique quotation number.

### Option B: Bulk generation using Excel

Allow the user to upload an Excel file containing multiple quotation records.

Provide a downloadable Excel template with the required columns and an example row.

Support multiple quotations in one Excel file. Use a unique quotation identifier to group line items belonging to the same quotation.

Suggested columns:

Quotation Number, Date, Customer Name, Customer Address, GSTIN, State, Vehicle Number, Item Description, GST Rate, Quantity, Unit, Rate, Due On, Remarks.

Validate the uploaded Excel file and show any errors before generating PDFs.

Allow the user to preview the imported quotations, make corrections where practical and generate all PDFs in one operation.

Package all generated PDFs into a single ZIP file for download.

Do not silently ignore invalid rows. Show useful validation errors, including the affected Excel row number.

## 7. Quotation history

Create a Quotation History page to maintain a local record of generated quotations.

Display a table with:

* Quotation Number
* Quotation Date
* Customer Name
* Vehicle Number
* Subtotal
* GST
* Grand Total
* Generation Date

Allow users to:

* Search by quotation number
* Filter by customer name
* Filter by date
* View quotation details
* Download an existing PDF, if it is stored
* Export quotation history to Excel

Store the quotation history locally using SQLite.

Do not overwrite an existing quotation with the same number without explicitly notifying the user and asking for confirmation.

## 8. Dashboard

Create a simple dashboard displaying:

* Total quotations generated
* Total quotation value
* Number of quotations generated this month
* Recent quotations
* Quick action to create a new quotation
* Quick action to generate bulk quotations

Calculate dashboard figures from the locally stored quotation history.

## 9. Validation and error handling

Implement comprehensive validation:

* Mandatory field validation
* Valid quotation date
* Valid customer details
* Positive quantity
* Non-negative rate
* Valid GST percentage
* At least one line item
* Valid quotation number
* Duplicate quotation number detection
* Valid Excel file format
* Missing or invalid Excel column detection

Use clear, user-friendly error messages.

Handle PDF generation errors gracefully.

Ensure the application does not generate an incomplete or corrupted PDF when validation fails.

## 10. Data storage

Use:

* JSON for company settings
* SQLite for quotation history
* Temporary in-memory data for unsaved quotation forms
* A local output directory for generated PDF files

Keep the project easy to back up and move to another computer.

Make sure uploaded Excel files and generated PDFs are handled safely.

Do not store sensitive information unnecessarily.

## 11. Project structure

Create the application with the following modular structure:

quotation_generator/
app.py
config.py
requirements.txt
README.md

```
modules/
    __init__.py
    company_settings.py
    quotation_form.py
    calculations.py
    pdf_generator.py
    bulk_generator.py
    excel_handler.py
    quotation_history.py
    database.py
    number_to_words.py
    validators.py

templates/
    quotation_template.py

data/
    company_settings.json
    quotations.db

output/
    .gitkeep

assets/
    .gitkeep
```

Separate the Streamlit UI, business logic, calculations and PDF generation.

Do not put the entire application into a single Python file.

Create any additional files needed to make the application reliable.

## 12. User experience

The UI should include:

* A clean sidebar navigation
* A professional page layout
* Expandable sections for customer, quotation and item details
* Dynamic item entry
* An immediate calculation summary
* A quotation preview before PDF generation
* Clear download buttons
* Useful validation and success messages

Use Streamlit session state to preserve form values when the UI reruns.

Avoid losing entered data when adding or removing items.

Make the application easy to operate on a normal Windows laptop using VS Code.

## 13. Testing

Create unit tests for:

* Item amount calculation
* CGST and SGST calculation
* IGST calculation
* Round-off calculation
* Total amount in words
* Quotation number generation
* Excel validation
* PDF generation
* Duplicate quotation validation

Include test cases that reproduce the totals from the attached sample quotations.

Sample quotation test 1:

* Item 1: 600
* Item 2: 1,500
* Item 3: 360
* Item 4: 1,000
* Subtotal: 3,460
* CGST: 311.40
* SGST: 311.40
* Round Off: 0.20
* Grand Total: 4,083

Sample quotation test 2:

* Item 1: 600
* Item 2: 1,000
* Item 3: 300
* Subtotal: 1,900
* CGST: 171
* SGST: 171
* Grand Total: 2,242

Use these examples to validate the calculation engine. Treat them as reference cases, not as fixed values in the application.

## 14. Documentation and execution

Create a complete README.md containing:

* Application overview
* Features
* Prerequisites
* Installation instructions
* Dependency installation
* How to run the application
* How to create a quotation
* How to generate multiple quotations
* How to upload an Excel file
* How to download PDFs and ZIP files
* How to change company settings
* How to run the tests
* Troubleshooting

Provide a requirements.txt file with all required dependencies.

The application must start using:

streamlit run app.py

Ensure the application runs locally without requiring a paid API, cloud account or external service.

## 15. Development instructions

Build the complete, working application rather than just providing a design or sample code.

First, inspect the two attached reference PDFs and identify their layout and fields. Then implement the application.

Create all required files in the current VS Code workspace.

Implement the application incrementally, but do not stop after creating the basic UI. Complete the PDF generator, calculations, bulk generation, data persistence and tests.

After implementation:

1. Review all files for missing imports and errors.
2. Install or list the required dependencies.
3. Run the unit tests.
4. Fix any issues identified.
5. Ensure the application starts successfully.
6. Explain how to run it and how to use each feature.

If a particular visual detail cannot be reproduced exactly from the reference PDFs, implement the closest practical equivalent and keep the PDF layout configurable.

**Final expectation:** A fully functional Python + Streamlit quotation generator that can create individual and bulk quotation PDFs, automatically calculate GST and totals, and maintain a local quotation history.
