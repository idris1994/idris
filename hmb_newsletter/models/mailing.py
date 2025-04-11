# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import threading
from ast import literal_eval
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from werkzeug.urls import url_join
from PIL import Image, UnidentifiedImageError

from odoo import api, fields, models, tools, _
from odoo.addons.base_import.models.base_import import ImportValidationError
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)
class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    def action_send_mail(self, res_ids=None):
        author_id = self.env.user.partner_id.id
        for mailing in self:
            for mailing_list in mailing.contact_list_ids:
                comp_name = mailing_list.company_id.name.replace(" ", "-") if mailing_list and mailing_list.company_id else "null"
                body = mailing._prepend_preview(mailing.body_html, mailing.preview).replace("#list_id#", comp_name)
                context_user = mailing.user_id or mailing.write_uid or self.env.user
                mailing = mailing.with_context(
                    **self.env['res.users'].with_user(context_user).context_get()
                )
                mailing_res_ids = res_ids or mailing._get_remaining_recipients()
                if not mailing_res_ids:
                    raise UserError(_('There are no recipients selected.'))

                composer_values = {
                    'auto_delete': not mailing.keep_archives,
                    # email-mode: keep original message for routing
                    'auto_delete_keep_log': mailing.reply_to_mode == 'update',
                    'author_id': author_id,
                    'attachment_ids': [(4, attachment.id) for attachment in mailing.attachment_ids],
                    'body': body,
                    'composition_mode': 'mass_mail',
                    'email_from': mailing.email_from,
                    'mail_server_id': mailing.mail_server_id.id,
                    'mailing_list_ids': [(4, mailing_list.id)],
                    'mass_mailing_id': mailing.id,
                    'model': mailing.mailing_model_real,
                    'record_name': False,
                    'reply_to_force_new': mailing.reply_to_mode == 'new',
                    'subject': mailing.subject,
                    'template_id': False,
                }
                if mailing.reply_to_mode == 'new':
                    composer_values['reply_to'] = mailing.reply_to

                composer = self.env['mail.compose.message'].with_context(
                    active_ids=mailing_res_ids,
                    default_composition_mode='mass_mail',
                    **mailing._get_mass_mailing_context()
                ).create(composer_values)

                # auto-commit except in testing mode
                composer._action_send_mail(
                    auto_commit=not getattr(threading.current_thread(), 'testing', False)
                )
                mailing.write({
                    'state': 'done',
                    'sent_date': fields.Datetime.now(),
                    # send the KPI mail only if it's the first sending
                    'kpi_mail_required': not mailing.sent_date,
                })
        return True


