# Angola Debit Notes & Origin Control (`dl_debit_note_ao`)

Unified Customer & Vendor Debit Note Management (**ND** & **NDF**) for Odoo **16.0, 17.0, 18.0, 19.0, and 20.0**, combining international Odoo standards with Angolan fiscal compliance (**AGT / SAF-T AO / Electronic Invoicing**).

## Key Features

1. **Automated ND & NDF Fiscal Journals (`_post_init_hook` & `account.journal`):**
   - Automatically provisions and configures the **Customer Debit Note (`ND`)** sales journal and **Vendor Debit Note (`NDF`)** purchase journal for each company.
   - Automatically sets `saft_inv_type = 'ND'` when `dl_certification_ao` is installed and disables duplicate `DND/` prefixing (`debit_sequence = False`).
   - Unlocks and organizes **Customers -> Debit Notes**, **Vendors -> Debit Notes**, and **Vendors -> Credit Notes** menus.

2. **Dual Issuance Workflow:**
   - **1-Click Wizard from Invoice/Credit Note:** Click **Debit Note (Nota de Debito)** on any posted document to launch the pre-filled wizard with automatic `ND`/`NDF` journal selection and optional line copying.
   - **Direct Creation from Dedicated Menus:** Create Debit Notes directly from **Customers -> Debit Notes** or **Vendors -> Debit Notes** with dynamic partner-filtered **Origin Invoice (`debit_origin_id`)** selection.

3. **Pre-Posting AGT Fiscal Validations (`action_post`):**
   - Enforces a mandatory **Origin Invoice (`debit_origin_id`)** that must be in `posted` state and belong to the same commercial partner.
   - Enforces a mandatory **Issuance Reason (`debit_note_reason` / `ref`)**.
   - Verifies that the Debit Note total amount is strictly positive (`amount_total > 0`).

4. **Full Angola Ecosystem Synchronization:**
   - Automatically synchronizes `debit_origin_id`, `invoice_origin`, `invoice_origin_id`, `ref`, and `reason_cancel` for seamless compatibility with `dl_certification_ao` (SAF-T AO), `dl_layouts_ao` (A4 PDF Reports), and `l10n_ao_fe` (Electronic Invoicing).
   - Automatically migrates legacy `origin_invoice_id` records to `debit_origin_id`.

---
Developed by **DIGITALUB ANGOLA, LDA** — [www.digitalub.ao](https://www.digitalub.ao) | `suporte@digitalub.ao`
