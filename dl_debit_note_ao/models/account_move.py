# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    debit_origin_id = fields.Many2one(
        "account.move",
        string="Fatura de Origem",
        readonly=False,
        copy=False,
        index="btree_not_null",
        domain="[('partner_id', '=', partner_id), ('state', '=', 'posted'), "
               "('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')), "
               "('debit_origin_id', '=', False)]",
        help="Selecione a fatura ou documento original que está a ser retificado por esta Nota de Débito."
    )
    debit_note_ids = fields.One2many(
        "account.move",
        "debit_origin_id",
        string="Notas de Débito",
        help="As Notas de Débito emitidas para esta fatura."
    )
    debit_note_count = fields.Integer(
        string="Número de Notas de Débito",
        compute="_compute_debit_count"
    )
    is_debit_note_journal = fields.Boolean(
        string="É Diário de Nota de Débito",
        compute="_compute_is_debit_note_journal",
        store=True,
    )
    debit_note_reason = fields.Char(
        string="Motivo da Nota de Débito",
        copy=False,
        help="Indique o motivo de emissão da Nota de Débito (obrigatório segundo as normas fiscais da AGT / SAF-T AO)."
    )

    @api.depends("debit_note_ids")
    def _compute_debit_count(self):
        for inv in self:
            inv.debit_note_count = len(inv.debit_note_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("default_is_debit_note"):
            company_id = res.get("company_id") or self.env.company.id
            move_type = res.get("move_type") or self.env.context.get("default_move_type") or "out_invoice"
            target_code = "NDF" if move_type in ("in_invoice", "in_refund") else "ND"
            target_type = "purchase" if move_type in ("in_invoice", "in_refund") else "sale"
            nd_journal = self.env["account.journal"].search([
                ("code", "=", target_code),
                ("company_id", "=", company_id),
            ], limit=1)
            if not nd_journal and "saft_inv_type" in self.env["account.journal"]._fields:
                nd_journal = self.env["account.journal"].search([
                    ("saft_inv_type", "=", "ND"),
                    ("type", "=", target_type),
                    ("company_id", "=", company_id),
                ], limit=1)
            if nd_journal:
                res["journal_id"] = nd_journal.id
        return res

    @api.depends("journal_id", "journal_id.code", "debit_origin_id")
    def _compute_is_debit_note_journal(self):
        for move in self:
            is_nd = bool(move.debit_origin_id)
            if move.journal_id:
                saft_type = (
                    move.journal_id.saft_inv_type
                    if "saft_inv_type" in move.journal_id._fields
                    else False
                )
                if move.journal_id.code in ("ND", "NDF") or saft_type == "ND":
                    is_nd = True
            move.is_debit_note_journal = is_nd

    def _format_debit_origin_name(self, origin_move):
        if not origin_move:
            return False
        origin_doc = (
            origin_move.internal_number
            if ("internal_number" in origin_move._fields and origin_move.internal_number)
            else origin_move.name
        ) or ""
        saft_type = (
            origin_move.journal_id.saft_inv_type
            if ("saft_inv_type" in origin_move.journal_id._fields and origin_move.journal_id.saft_inv_type)
            else False
        )
        if saft_type and origin_doc and not origin_doc.startswith(saft_type):
            origin_doc = f"{saft_type} {origin_doc}"
        return origin_doc

    @api.onchange("partner_id")
    def _onchange_partner_id_clear_debit_origin(self):
        for move in self:
            if move.debit_origin_id and move.partner_id:
                if move.debit_origin_id.commercial_partner_id != move.partner_id.commercial_partner_id:
                    move.debit_origin_id = False

    @api.onchange("debit_origin_id", "debit_note_reason")
    def _onchange_debit_origin_sync_fields(self):
        for move in self:
            if move.debit_origin_id:
                origin_doc = move._format_debit_origin_name(move.debit_origin_id)
                move.invoice_origin = origin_doc
                if "invoice_origin_id" in move._fields:
                    move.invoice_origin_id = move.debit_origin_id.id
            if move.debit_note_reason:
                move.ref = move.debit_note_reason
                if "reason_cancel" in move._fields:
                    move.reason_cancel = move.debit_note_reason[:64]

    def _sync_debit_note_fields(self):
        for move in self:
            if not move.is_debit_note_journal and not move.debit_origin_id:
                continue

            if "invoice_origin_id" in move._fields:
                if move.debit_origin_id and not move.invoice_origin_id:
                    move.invoice_origin_id = move.debit_origin_id.id
                elif move.invoice_origin_id and not move.debit_origin_id and move.is_debit_note_journal:
                    move.debit_origin_id = move.invoice_origin_id.id

            if move.debit_origin_id:
                origin_doc = move._format_debit_origin_name(move.debit_origin_id)
                if origin_doc and move.invoice_origin != origin_doc:
                    move.invoice_origin = origin_doc

            reason = move.debit_note_reason or move.ref or (
                move.reason_cancel if "reason_cancel" in move._fields else False
            )
            if reason:
                if not move.debit_note_reason:
                    move.debit_note_reason = reason
                if not move.ref:
                    move.ref = reason
                if "reason_cancel" in move._fields and not move.reason_cancel:
                    move.reason_cancel = reason[:64]

    def action_post(self):
        self._sync_debit_note_fields()
        for move in self:
            is_nd_doc = (
                move.move_type in ("out_invoice", "in_invoice")
                and (move.is_debit_note_journal or bool(move.debit_origin_id))
            )
            if is_nd_doc:
                if not move.debit_origin_id:
                    raise ValidationError(_(
                        "Com o diário de 'Nota de Débito' selecionado, o campo 'Fatura de Origem' "
                        "deve ser obrigatoriamente preenchido."
                    ))
                if move.debit_origin_id.state != "posted":
                    raise ValidationError(_(
                        "A Fatura de Origem (%s) deve estar publicada (confirmada) e não pode estar "
                        "anulada ou em rascunho."
                    ) % move.debit_origin_id.display_name)
                if move.debit_origin_id.commercial_partner_id != move.commercial_partner_id:
                    raise ValidationError(_(
                        "A Fatura de Origem (%s) pertence a outro parceiro (%s). "
                        "A Nota de Débito deve ser emitida para o mesmo cliente/fornecedor da fatura original."
                    ) % (move.debit_origin_id.display_name, move.debit_origin_id.partner_id.display_name))
                if not move.debit_note_reason and not move.ref:
                    raise ValidationError(_(
                        "O campo 'Motivo da Nota de Débito' é de preenchimento obrigatório "
                        "para a emissão de Notas de Débito (norma AGT / SAF-T AO)."
                    ))
                if move.amount_total <= 0:
                    raise ValidationError(_(
                        "O valor total de uma Nota de Débito deve ser estritamente superior a zero."
                    ))
        return super().action_post()

    def action_view_debit_notes(self):
        self.ensure_one()
        view_mode = "tree,form" if int(odoo_release_major()) < 18 else "list,form"
        return {
            "type": "ir.actions.act_window",
            "name": _("Notas de Débito"),
            "res_model": "account.move",
            "view_mode": view_mode,
            "domain": [("debit_origin_id", "=", self.id)],
        }

    def action_debit_note(self):
        self.ensure_one()
        return {
            "name": _("Emitir Nota de Débito"),
            "res_model": "account.debit.note",
            "view_mode": "form",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "active_model": "account.move",
                "active_ids": self.ids,
            },
        }

    def _get_debit_note_origin(self):
        self.ensure_one()
        return self.debit_origin_id

    def _get_starting_sequence(self):
        starting_sequence = super()._get_starting_sequence()
        if (
            self.journal_id
            and self.journal_id.code in ("ND", "NDF")
            and starting_sequence.startswith("DND")
        ):
            starting_sequence = starting_sequence[1:]
        return starting_sequence


def odoo_release_major():
    from odoo import release
    return str(release.version_info[0]) if hasattr(release, "version_info") else "17"
