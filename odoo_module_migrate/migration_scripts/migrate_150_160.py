# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_TEXT_REPLACES = {
    ".py": {
        r"\.get_xml_id\(": ".get_external_id(",
        r"\.fields_get_keys\(\)": "._fields",
    },
}


class MigrationScript(BaseMigrationScript):
    _TEXT_REPLACES = _TEXT_REPLACES
