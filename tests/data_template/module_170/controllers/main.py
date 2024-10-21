from odoo import http
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.http import request


class MainController(http.Controller):
    @http.route("/home/main", type="http", auth="public", website=True)
    def redirect_to_main(self):
        current_partner = request.env.user.partner_id
        partner_name = slugify(current_partner.name) or ""
        return f"<h1 style='color: blue;'>Hello {partner_name}</h1>"
