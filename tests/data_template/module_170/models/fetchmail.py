from odoo import models, tools, _
from odoo.tools import misc
from odoo.tools import ustr
from odoo.tools.misc import ustr
from odoo.tools.misc import ustr, find_in_path
from odoo.tools import ustr, config, consteq, file_path
from odoo.tools.misc import lazy, ustr
from odoo.tools import config, consteq, ustr, file_path
from ssl import SSLError
from odoo.exceptions import UserError


class FetchMailServer(models.Model):
    _inherit = "fetchmail.server"

    def example_method_use_ustr(self):
        try:
            server_name = ustr(self.name)
            description = misc.ustr(self._description)
            connection = self.connect(allow_archived=True)
        except SSLError as e:
            raise UserError(_(tools.ustr(e)))
