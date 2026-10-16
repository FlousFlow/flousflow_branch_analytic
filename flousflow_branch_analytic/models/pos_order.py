from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_account_move_line_data(self, aggregate=True):
        """Tag POS revenue lines for invoices and session-closing moves."""
        lines = super()._prepare_account_move_line_data(aggregate=aggregate)
        for line_data in lines:
            vals = line_data.get('account.move.line', {})
            if vals.get('display_type') != 'product' or not vals.get('product_id'):
                continue
            metadata = line_data.get('metadata', {})
            pos_line = metadata.get('line')
            if pos_line is None:
                pos_line = metadata.get('base_line', {}).get('record')
            order = pos_line.order_id if pos_line else self[:1]
            account = order.config_id.analytic_account_id if order else False
            if account:
                vals['analytic_distribution'] = {str(account.id): 100.0}
        return lines

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        account = self.config_id.analytic_account_id
        if account:
            vals['analytic_account_id'] = account.id
        return vals
