from odoo import models, tools, _
from odoo.tools import misc
from odoo.tools.misc import find_in_path
from odoo.tools import config, consteq, file_path
from odoo.tools.misc import lazy
from odoo.tools import config, consteq, file_path
from ssl import SSLError
from odoo.exceptions import UserError


class FetchMailServer(models.Model):
    _inherit = "fetchmail.server"

    def example_method_use_ustr(self):
        try:
            server_name = self.name
            description = self._description
            connection = self.connect(allow_archived=True)
        except SSLError as e:
            raise UserError(_(e))
