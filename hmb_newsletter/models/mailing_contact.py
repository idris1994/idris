from odoo import models, fields

class MassMailingContact(models.Model):
    _inherit = 'mailing.contact'

    company_ids = fields.Many2many("res.company")