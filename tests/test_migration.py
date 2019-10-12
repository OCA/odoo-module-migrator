# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from filecmp import dircmp
import os
import shutil
import unittest

from odoo_migrate.migration import Migration


class TestConfig(unittest.TestCase):

    def test_migration(self):
        template_path = "./tests/data_template"
        working_path = "./tests/data_tmp"
        expected_path = "./tests/data_result"
        module_name = "module_8"
        result_name = "module_8_13"
        shutil.rmtree(working_path, ignore_errors=True)
        shutil.copytree(template_path, working_path)

        migration = Migration(
            working_path, "8.0", "13.0", [module_name], commit_enabled=False)
        migration.run()
        diff_files = dircmp(
            os.path.join(expected_path, result_name),
            os.path.join(working_path, module_name)).diff_files

        self.assertEqual(len(diff_files), 0)
