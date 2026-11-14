# -*- coding: utf-8 -*-
{
    "name": "Angola Debit Notes & Origin Control (Nota de Débito AGT)",
    "version": "16.0.1.0.1",
    "summary": "Unified Customer & Vendor Debit Notes (ND/NDF), Mandatory Origin Invoice, Reason Control & Angola AGT SAF-T Compliance",
    "description": """
Angola Debit Notes & Origin Control (Nota de Debito AGT)
========================================================

Unified Customer & Vendor Debit Note module combining international Odoo accounting standards with Angolan fiscal compliance (AGT / SAF-T AO / Electronic Invoicing):
- Automatic provisioning and configuration of Customer Debit Note (ND) and Vendor Debit Note (NDF) journals with SAF-T type ND.
- Dual issuance workflow:
  1. Generate Debit Notes in 1 click directly from a posted Invoice or Credit Note via Wizard (pre-selects ND/NDF journal and copies lines).
  2. Create Debit Notes directly from Customers -> Debit Notes or Vendors -> Debit Notes menus with dynamic partner-filtered Origin Invoice selection.
- Mandatory pre-posting validation of Origin Invoice (must be posted and belong to the same commercial partner), Issuance Reason (Motivo), and strictly positive total amount.
- Seamless field synchronization with Angolan PDF Invoice Layouts (dl_layouts_ao), AGT Certification (dl_certification_ao), and Electronic Invoicing (l10n_ao_fe).
- 100% compatible with Odoo 16.0, 17.0, 18.0, 19.0 & 20.0 (Community, Enterprise & Odoo.sh).
    """,
    "author": "DIGITALUB ANGOLA, LDA",
    "website": "https://www.digitalub.ao",
    "support": "suporte@digitalub.ao",
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_debit_note_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "OPL-1",
    "post_init_hook": "_post_init_hook",
    "price": 45.0,
    "currency": "EUR",
    "images": [
        "static/description/banner.png",
        "static/description/step1_nd_journals.png",
        "static/description/step2_nd_wizard.png",
        "static/description/step3_nd_origin_control.png",
    ],
}
