# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re

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
        r"\._find_partner_from_emails\(": "._mail_find_partner_from_emails(",
        r"\._search_on_partner\(": "._mail_search_on_partner(",
        r"\._search_on_user\(": "._mail_search_on_user(",
    },
    ".xml": {
        r"( |\t)*<field name=('|\")view_type('|\")>.*</field>\n": "",
        r"src_model": "binding_model",
        re.compile(
            r"""
            # find a button...
            <button
                \s[^>]*
                # ... that is a oe_stat_button
                class=['"].*\b
                    oe_stat_button
                \b.*['"]
                [^>]*>\s*
                    # ... that contains a field
                    <field\s+
                        (
                            [^>]*
                            (
                                # ...  named "active"
                                name=['"]active['"]|
                                # ... with a boolean_button widget
                                widget=['"]boolean_button['"]
                            )
                            [^>]*
                        ){2}
                    [^>]*>\s*
            </button>
            """,
            re.VERBOSE,
        ): """
            <field name="active" invisible="1" />
            <widget
                name="web_ribbon"
                title="Archived"
                bg_color="bg-danger"
                attrs="{'invisible': [('active', '=', True)]}"
            />
            """,
    },
}
