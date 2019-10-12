# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from filecmp import dircmp
import os
import pathlib
import shutil
import unittest

from odoo_migrate.__main__ import main


class TestMigration(unittest.TestCase):

    _template_path = pathlib.Path("./tests/data_template").resolve()
    _working_path = pathlib.Path("./tests/data_tmp").resolve()
    _expected_path = pathlib.Path("./tests/data_result").resolve()

    def _migrate_module_diff_result(
        self, module_name, result_name, init_version_name, target_version_name
    ):
        shutil.rmtree(self._working_path, ignore_errors=True)
        shutil.copytree(self._template_path, self._working_path)

        main([
            "--directory", str(self._working_path),
            "--init-version-name", init_version_name,
            "--target-version-name", target_version_name,
            "--modules", module_name,
            "--log-path", str(self._working_path / "test_log.log"),
            "--no-commit",
        ])

        return dircmp(
            os.path.join(self._expected_path, result_name),
            os.path.join(self._working_path, module_name)).diff_files

    def test_migration_080_130(self):
        diff_files = self._migrate_module_diff_result(
            "module_080", "module_080_130", "8.0", "13.0")
        import pdb; pdb.set_trace()
        self.assertEqual(len(diff_files), 0)
