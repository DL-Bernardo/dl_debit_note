# -*- coding: utf-8 -*-
{
    "name": "Angola Debit Notes & Origin Control (Nota de Débito AGT)",
    "version": "19.0.1.0.0",
    "summary": "Unified Debit Note Management (ND) with Mandatory Origin Invoice, Reason Control & AGT SAF-T AO Compliance",
    "description": """
Angola Debit Notes & Origin Control (Nota de Débito AGT)
========================================================

Unified module combining international Odoo Debit Note standards with Angolan fiscal compliance (AGT / SAF-T AO / Electronic Invoicing):
- Automatic creation and configuration of the ND (Nota de Débito) sales journal with SAF-T type ND.
- Dual workflow supported:
  1. Generate Debit Note directly from a posted Invoice or Credit Note via Wizard (pre-selects ND journal and copies lines).
  2. Create Debit Note manually from Customers -> Debit Notes menu with dynamic client-filtered Origin Invoice selection.
- Mandatory validation of Origin Invoice (must be posted and belong to the same customer), Issuance Reason (Motivo), and positive total amount upon posting.
- Seamless synchronization with Angolan PDF Invoice Layouts (dl_layouts_ao), AGT Certification (dl_certification_ao), and Electronic Invoicing (l10n_ao_fe).
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
    "license": "LGPL-3",
    "post_init_hook": "_post_init_hook",
    "price": 35.0,
    "currency": "USD",
    "images": ["static/description/banner.png"],
}
