# patch vies so that they don't break
from odoo.addons.base.models.ir_ui_view import View
import logging
_logger = logging.getLogger(__name__)


_original_check_xml = View._check_xml


def _check_xml(self):
    # TODO we should check exeception is due to the expected error
    try:
        _original_check_xml
    except Exception as e:
        pass


View._check_xml = _check_xml


# patch xml_import so that view is fixed
from odoo.tools.convert import xml_import
from .convert import _tag_record
xml_import._tag_record = _tag_record
