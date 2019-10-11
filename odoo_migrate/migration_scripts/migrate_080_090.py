# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

_TEXT_REPLACES = {
    "*": {
        "base.group_configuration": "base.group_system",
        "base.group_sale_salesman": "sales_team.group_sale_salesman",
        "base.group_sale_salesman_all_leads":
        "sales_team.group_sale_salesman_all_leads",
        "base.group_sale_manager": "sales_team.group_sale_manager",
    },
    ".py": {"select=True": "index=True"},
}
