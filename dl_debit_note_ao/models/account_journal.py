# -*- coding: utf-8 -*-
from odoo import models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model_create_multi
    def create(self, vals_list):
        has_saft_type = "saft_inv_type" in self._fields
        has_debit_seq = "debit_sequence" in self._fields
        for vals in vals_list:
            if vals.get("code") in ("ND", "NDF"):
                if has_saft_type and not vals.get("saft_inv_type"):
                    vals["saft_inv_type"] = "ND"
                if has_debit_seq and "debit_sequence" not in vals:
                    vals["debit_sequence"] = False
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if "code" in vals and vals.get("code") in ("ND", "NDF"):
            has_saft_type = "saft_inv_type" in self._fields
            for journal in self.filtered(lambda j: j.code in ("ND", "NDF")):
                if has_saft_type and journal.saft_inv_type != "ND":
                    journal.saft_inv_type = "ND"
        return res
