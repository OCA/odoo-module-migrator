# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

_TEXT_REPLACES = {
    ".py": {
        "from odoo.addons.base.res": "from odoo.addons.base.models",
        "from odoo.addons.base.ir": "from odoo.addons.base.models",
    }
}
