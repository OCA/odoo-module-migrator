# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_TEXT_REPLACES = {".py": {r"# (-\*- )?coding: utf-8( -\*-)?\n": ""}}


class MigrationScript(BaseMigrationScript):

    _TEXT_REPLACES = _TEXT_REPLACES
