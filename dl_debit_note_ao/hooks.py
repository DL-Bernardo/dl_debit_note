# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _post_init_hook(*args):
    if len(args) == 1:
        env = args[0]
    else:
        cr, registry = args[0], args[1]
        env = api.Environment(cr, SUPERUSER_ID, {})

    # Deactivate core account_debit_note form view if present to prevent duplicate fields in Odoo 16-20
    core_view = env.ref("account_debit_note.view_move_form_debit", raise_if_not_found=False)
    if core_view and core_view.active:
        core_view.sudo().write({"active": False})

    Journal = env["account.journal"].sudo()
    Account = env["account.account"].sudo()
    has_saft_type = "saft_inv_type" in Journal._fields
    has_debit_seq = "debit_sequence" in Journal._fields
    has_refund_seq = "refund_sequence" in Journal._fields

    companies = env["res.company"].sudo().search([])
    for company in companies:
        domain_company = [("company_id", "=", company.id)] if "company_id" in Account._fields else [("company_ids", "in", company.id)]

        # 1. Customer Debit Note Journal (ND - sale)
        journal_nd = Journal.search([
            ("code", "=", "ND"),
            ("company_id", "=", company.id),
        ], limit=1)
        if journal_nd:
            update_vals = {}
            if has_saft_type and journal_nd.saft_inv_type != "ND":
                update_vals["saft_inv_type"] = "ND"
            if has_debit_seq and journal_nd.debit_sequence:
                update_vals["debit_sequence"] = False
            if update_vals:
                with env.cr.savepoint():
                    try:
                        journal_nd.write(update_vals)
                    except Exception:
                        pass
        else:
            income_account = Account.search(domain_company + [("account_type", "=", "income")], limit=1)
            if not income_account:
                income_account = Account.search(domain_company + [("account_type", "=", "income_other")], limit=1)
            nd_vals = {
                "name": "Nota de Débito",
                "type": "sale",
                "code": "ND",
                "company_id": company.id,
            }
            if income_account:
                nd_vals["default_account_id"] = income_account.id
            if has_saft_type:
                nd_vals["saft_inv_type"] = "ND"
            if has_debit_seq:
                nd_vals["debit_sequence"] = False
            if has_refund_seq:
                nd_vals["refund_sequence"] = True
            with env.cr.savepoint():
                try:
                    Journal.with_company(company).create(nd_vals)
                except Exception:
                    pass

        # 2. Vendor Debit Note Journal (NDF - purchase)
        journal_ndf = Journal.search([
            ("code", "=", "NDF"),
            ("company_id", "=", company.id),
        ], limit=1)
        if journal_ndf:
            update_vals = {}
            if has_saft_type and journal_ndf.saft_inv_type != "ND":
                update_vals["saft_inv_type"] = "ND"
            if has_debit_seq and journal_ndf.debit_sequence:
                update_vals["debit_sequence"] = False
            if update_vals:
                with env.cr.savepoint():
                    try:
                        journal_ndf.write(update_vals)
                    except Exception:
                        pass
        else:
            expense_account = Account.search(domain_company + [("account_type", "=", "expense")], limit=1)
            if not expense_account:
                expense_account = Account.search(domain_company + [("account_type", "=", "expense_direct_cost")], limit=1)
            ndf_vals = {
                "name": "Nota de Débito de Fornecedor",
                "type": "purchase",
                "code": "NDF",
                "company_id": company.id,
            }
            if expense_account:
                ndf_vals["default_account_id"] = expense_account.id
            if has_saft_type:
                ndf_vals["saft_inv_type"] = "ND"
            if has_debit_seq:
                ndf_vals["debit_sequence"] = False
            if has_refund_seq:
                ndf_vals["refund_sequence"] = True
            with env.cr.savepoint():
                try:
                    Journal.with_company(company).create(ndf_vals)
                except Exception:
                    pass

    # Migrate legacy custom_debit_note_origin (origin_invoice_id -> debit_origin_id) if column exists
    env.cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'account_move' AND column_name = 'origin_invoice_id'
    """)
    if env.cr.fetchone():
        env.cr.execute("""
            UPDATE account_move
            SET debit_origin_id = origin_invoice_id
            WHERE debit_origin_id IS NULL AND origin_invoice_id IS NOT NULL
        """)
