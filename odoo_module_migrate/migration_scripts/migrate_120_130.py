# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

_TEXT_WARNINGS = {
    ".xml": {
        r'active.*widget="toggle_button"|widget="toggle_button".*active|'
        r'widget="boolean_button".*active|active.*widget="boolean_button"':
        'You can remove actions archive/unarchive'
    },
    ".py": {
        r".*oldname":
            "oldname is not supported yet. Create a migration script",
        r"digits=[^, )]*get_precision":
            'You can use string to qualify type of '
            'precision without import nothing'
    },
}

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
    },
    ".xml": {
        r"( |\t)*<field name=('|\")view_type('|\")>.*</field>\n": "",
        r"src_model": "binding_model",
    }
}
