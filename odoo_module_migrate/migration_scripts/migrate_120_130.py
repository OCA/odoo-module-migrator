# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

_TEXT_ERRORS = {
    "*": {
        "web_settings_dashboard":
        "[V13] Reference to 'web_settings_dashboard'"
        ". This module has been removed."
    },
    ".py": {
        r".*@api.returns.*\n":
        "[13] Use of deprecated decorator '@api.returns'",
        r".*@api.cr.*\n":
        "[13] Use of deprecated decorator '@api.cr'",
        r".*@api.model_cr.*\n":
        "[13] Use of deprecated decorator '@api.model_cr'",
    },
}

_TEXT_REPLACES = {
    ".py": {
        r".*@api.multi.*\n": "",
        r".*@api.one.*\n": "",
        r"\.sudo\((?P<user>[^/)]+?)\)": r".with_user(\g<user>)",
        r"\.suspend_security": ".sudo",
        r"\"base_suspend_security\",\n": "",
        r"self.env.user.company_id": r"self.env.company"
    },
    ".xml": {
        r"( |\t)*<field name=('|\")view_type('|\")>.*</field>\n": "",
        r"( |\t)*<field name=('|\")domain_force('|\")>"
        r".*company_id.*child_of.*</field>\n":
            r"\t\t<field name=\2domain_force\2>"
            r"['|',('company_id','=',False),"
            r"('company_id', 'in', company_ids)]</field>\n"
    }
}
