from odoo import models, fields

class MassMailingList(models.Model):
    _inherit = 'mailing.list'

    company_id = fields.Many2one("res.company", string="Company")