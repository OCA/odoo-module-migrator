# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_REMOVED_FIELDS = [
    ('product.product', 'price',
        'Commit https://github.com/odoo/odoo/commit/9e99a9df464d97a74ca320d')
]

_TEXT_REPLACES = {
    ".py": {
        r"\.get_xml_id\(": ".get_external_id(",
        r"\.fields_get_keys\(\)": "._fields",
    },
}


class MigrationScript(BaseMigrationScript):
    _TEXT_REPLACES = _TEXT_REPLACES
    _REMOVED_FIELDS = _REMOVED_FIELDS
