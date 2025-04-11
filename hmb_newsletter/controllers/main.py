from odoo import tools, _
from odoo.http import route, request
from odoo.addons.mass_mailing.controllers import main

class MassMailControllerInherit(main.MassMailController):

    @route('/website_mass_mailing/subscribe', type='json', website=True, auth='public')
    def subscribe(self, list_id, value, subscription_type, **post):

        active_store = request.session.get('dynamic_top_menu', {})
        store_id = f'{active_store.get("name")} Newsletter Store'

        if not active_store:
            list_id = list_id

        else :
            lists = request.env['mailing.list'].sudo().search(
                [('company_id', '=', int(active_store.get("id")))], limit=1
            )
            if not lists:
                lists = request.env['mailing.list'].sudo().create(
                    {'name':store_id, "company_id":active_store.get("id")}
                )
            list_id = lists.id
        return_val = super().subscribe(list_id, value, subscription_type, **post)

        Contacts = request.env['mailing.contact'].sudo()
        fname = self._get_fname(subscription_type)
        contact_id = Contacts.search([(fname, '=', value)], limit=1)

        companies = contact_id.company_name if contact_id else "[]"

        try:
            companies = eval(companies)
        except:
            companies = [companies] if companies else []

        companies.append(active_store.get("name", False) or "homemadeby")
        companies = list(set(companies))

        company = request.env["res.company"].sudo().search([("id", "=", active_store.get("id"))], limit=1)

        if company:
            contact_id.write({
                "company_ids": [(4, company.id)],
                "company_name": ", ".join(companies)
            })

        return return_val
