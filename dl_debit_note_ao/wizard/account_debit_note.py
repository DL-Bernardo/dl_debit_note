# -*- coding: utf-8 -*-
from odoo import models, fields, api, release, _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):
    _name = "account.debit.note"
    _description = "Add Debit Note wizard"

    move_ids = fields.Many2many(
        "account.move",
        "account_move_debit_move",
        "debit_id",
        "move_id",
        domain=[("state", "=", "posted")],
    )
    date = fields.Date(
        string="Data da Nota de Débito",
        default=fields.Date.context_today,
        required=True,
    )
    reason = fields.Char(
        string="Motivo da Nota de Débito",
        required=True,
        help="Indique o motivo de emissão da Nota de Débito (obrigatório segundo as normas fiscais da AGT).",
    )

    def _default_nd_journal(self):
        active_ids = self.env.context.get("active_ids", [])
        moves = (
            self.env["account.move"].browse(active_ids)
            if self.env.context.get("active_model") == "account.move" and active_ids
            else self.env["account.move"]
        )
        company = moves[0].company_id if moves else self.env.company
        is_purchase = bool(moves and any(m.move_type in ("in_invoice", "in_refund") for m in moves))
        target_code = "NDF" if is_purchase else "ND"
        target_type = "purchase" if is_purchase else "sale"

        Journal = self.env["account.journal"]
        journal = Journal.search([
            ("code", "=", target_code),
            ("company_id", "=", company.id),
        ], limit=1)
        if not journal and "saft_inv_type" in Journal._fields:
            journal = Journal.search([
                ("saft_inv_type", "=", "ND"),
                ("type", "=", target_type),
                ("company_id", "=", company.id),
            ], limit=1)
        return journal

    journal_id = fields.Many2one(
        "account.journal",
        string="Diário da Nota de Débito",
        default=_default_nd_journal,
        help="Se vazio, utiliza o diário de Nota de Débito (ND / NDF) da empresa ou o diário da fatura original.",
    )
    copy_lines = fields.Boolean(
        "Copiar Linhas",
        default=True,
        help="Copia as linhas da fatura original para facilitar a retificação.",
    )
    move_type = fields.Char(compute="_compute_from_moves")
    journal_type = fields.Char(compute="_compute_from_moves")
    country_code = fields.Char(related="move_ids.company_id.country_id.code")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_ids = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move" and self.env.context.get("active_ids")
            else self.env["account.move"]
        )
        if any(move.state != "posted" for move in move_ids):
            raise UserError(_("Apenas pode emitir Notas de Débito para faturas publicadas."))
        elif any(move.debit_origin_id for move in move_ids):
            raise UserError(_("Não é possível emitir uma Nota de Débito a partir de um documento que já é uma Nota de Débito."))
        elif any(move.move_type not in ["out_invoice", "in_invoice", "out_refund", "in_refund"] for move in move_ids):
            raise UserError(_("Apenas pode emitir Notas de Débito para Faturas ou Notas de Crédito."))
        if "move_ids" in fields_list or not fields_list:
            res["move_ids"] = [(6, 0, move_ids.ids)]
        if not res.get("journal_id"):
            nd_journal = self._default_nd_journal()
            if nd_journal:
                res["journal_id"] = nd_journal.id
        return res

    @api.depends("move_ids")
    def _compute_from_moves(self):
        for record in self:
            move_ids = record.move_ids
            record.move_type = (
                move_ids[0].move_type
                if len(move_ids) == 1 or not any(m.move_type != move_ids[0].move_type for m in move_ids)
                else False
            )
            record.journal_type = (
                "purchase" if record.move_type in ["in_refund", "in_invoice"] else "sale"
            )

    def _prepare_debit_note_vals(self, move):
        return {}

    def _prepare_default_values(self, move):
        if move.move_type in ("in_refund", "out_refund"):
            move_type = "in_invoice" if move.move_type == "in_refund" else "out_invoice"
        else:
            move_type = move.move_type

        journal_id = self.journal_id.id if self.journal_id else False
        if not journal_id:
            nd_journal = self._default_nd_journal()
            if nd_journal:
                journal_id = nd_journal.id
        if not journal_id:
            journal_id = move.journal_id.id

        origin_doc = (
            move._format_debit_origin_name(move)
            if hasattr(move, "_format_debit_origin_name")
            else (move.name or "")
        )
        reason_text = self.reason or _("Retificação / Nota de Débito")

        default_values = {
            "ref": reason_text,
            "debit_note_reason": reason_text,
            "invoice_origin": origin_doc,
            "date": self.date or move.date,
            "invoice_date": move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            "journal_id": journal_id,
            "invoice_payment_term_id": None,
            "debit_origin_id": move.id,
            "move_type": move_type,
        }
        if not self.copy_lines or move.move_type in ("in_refund", "out_refund"):
            default_values["line_ids"] = [(5, 0, 0)]
        if "invoice_origin_id" in move._fields:
            default_values["invoice_origin_id"] = move.id
        if "reason_cancel" in move._fields:
            default_values["reason_cancel"] = reason_text[:64]

        extra_vals = self._prepare_debit_note_vals(move)
        if extra_vals:
            default_values.update(extra_vals)
        return default_values

    def create_debit(self):
        self.ensure_one()
        new_moves = self.env["account.move"]
        for move in self.move_ids.with_context(include_business_fields=True):
            default_values = self._prepare_default_values(move)
            new_move = move.copy(default=default_values)
            if hasattr(move, "_get_html_link"):
                move_msg = _("Esta Nota de Débito foi criada a partir de: %s", move._get_html_link())
            else:
                move_msg = _("Esta Nota de Débito foi criada a partir de: %s") % (move.name or "")
            new_move.message_post(body=move_msg)
            new_moves |= new_move

        major_ver = int(release.version_info[0]) if hasattr(release, "version_info") else 17
        list_mode = "tree,form" if major_ver < 18 else "list,form"
        action = {
            "name": _("Notas de Débito"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "context": {"default_move_type": default_values["move_type"]},
        }
        if len(new_moves) == 1:
            action.update({
                "view_mode": "form",
                "res_id": new_moves.id,
            })
        else:
            action.update({
                "view_mode": list_mode,
                "domain": [("id", "in", new_moves.ids)],
            })
        return action
