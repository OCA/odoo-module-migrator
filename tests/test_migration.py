# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from filecmp import dircmp
import pathlib
import shutil
import unittest

from odoo_migrate.__main__ import main


class TestMigration(unittest.TestCase):

    _template_path = pathlib.Path("./tests/data_template").resolve()
    _working_path = pathlib.Path("./tests/data_tmp").resolve()
    _expected_path = pathlib.Path("./tests/data_result").resolve()

    def _migrate_module(
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

    def _get_comparison(self, module_name, result_name):
        comparison = dircmp(
            str(self._expected_path / result_name),
            str(self._working_path / module_name))
        return comparison

    def _get_diff_files(self, comparison, folder):
        res = [os.path.join(folder, x) for x in comparison.diff_files]
        for subfolder, subcomparison in comparison.subdirs.items():
            res += self._get_diff_files(
                subcomparison, os.path.join(folder, subfolder))
        return res

    def test_migration_080_130(self):
        self._migrate_module("module_080", "module_080_130", "8.0", "13.0")
        comparison = self._get_comparison("module_080", "module_080_130")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files), 0,
            "Differences found in the following files\n- %s" % (
                "\n- ".join(diff_files)))

        # TODO test that log contains correct warning, and error message
