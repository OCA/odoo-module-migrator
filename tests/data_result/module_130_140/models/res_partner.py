# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    def test_improve_translation(self):
        return _("It's %s", 2024)
    
    def test_improve_transalation_with_line_break(self):
        raise ValidationError(
            _("The '%s' is empty or 0. It should have a non-null value.", "Price")
        )
    
    def test_improve_translation_with_parenthesis(self):
        return _("It's %s", 2024)
    
    def test_improve_translation_with_single_quote(self):
        return _('It is %s', 2024)
    
    def test_improve_translation_with_parenthesis_and_line_break(self):
        raise ValidationError(
            _("%s are only valid until %s", "User", 2024)
        )
    
    def test_improve_translation_with_brackets(self):
        return _("User %(name)s has %(items)s items", name="Dev", items=5)
    
    def test_improve_translation_with_single_quote(self):
        return _('User %(name)s has %(items)s items', name='Dev', items=5)
    
    def test_improve_translation_with_brackets_and_line_break(self):
        return _("User %(name)s has %(items)s items", name="Dev", items=5)
    
    def test_improve_translation_with_format(self):
        return _("It's %s", 2024)
    
    def test_improve_translation_with_format_and_single_quote(self):
        return _('It is %s', 2024)
    
    def test_improve_translation_with_format_and_line_break(self):
        return _("It's %s", 2024)
    
    def test_improve_translation_with_format_has_end_comma(self):
        return _("It's %s", 2024)
    
    def test_improve_translation_with_format_multi_params(self):
        return _("User %(name)s has %(items)s items", name="Dev", items=5)
    
    def test_improve_translation_with_format_multi_params_and_line_break(self):
        return _("User %(name)s has %(items)s items", name="Dev", items=5)
    
    def test_improve_translation_with_format_multi_params_has_end_comma(self):
        return _('User %(name)s has "acb" %(items)s items', name="Dev", items=5)
    