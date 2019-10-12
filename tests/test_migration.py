# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import shutil


import unittest
from odoo_migrate.migration import Migration


class TestConfig(unittest.TestCase):

    def test_migration(self):
        template_path = "./tests/data_template"
        working_path = "./tests/data_tmp"
        # expecting_path = "./tests/data_expected"
        shutil.rmtree(working_path, ignore_errors=True)
        shutil.copytree(template_path, working_path)
        migration = Migration(
            working_path, "8.0", "13.0", commit_enabled=False)
        migration.run()
