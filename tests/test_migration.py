# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import re
from filecmp import dircmp
import pathlib
import shutil
import unittest

from odoo_module_migrate.__main__ import main
from odoo_module_migrate.tools import _read_content


class TestMigration(unittest.TestCase):

    _template_path = pathlib.Path("./tests/data_template").resolve()
    _working_path = pathlib.Path("./tests/data_tmp").resolve()
    _expected_path = pathlib.Path("./tests/data_result").resolve()

    def _migrate_module(
        self, module_name, result_name, init_version_name, target_version_name
    ):
        shutil.rmtree(self._working_path, ignore_errors=True)
        shutil.copytree(self._template_path, self._working_path)

        main(
            [
                "--directory",
                str(self._working_path),
                "--init-version-name",
                init_version_name,
                "--target-version-name",
                target_version_name,
                "--modules",
                module_name,
                "--log-path",
                str(self._working_path / "test_log.log"),
                "--no-commit",
            ]
        )

    def _get_comparison(self, module_name, result_name):
        comparison = dircmp(
            str(self._expected_path / result_name),
            str(self._working_path / module_name),
        )
        return comparison

    def _get_diff_files(self, comparison, folder):
        res = [os.path.join(folder, x) for x in comparison.diff_files]
        for subfolder, subcomparison in comparison.subdirs.items():
            res += self._get_diff_files(subcomparison, os.path.join(folder, subfolder))
        return res

    def test_migration_080_130(self):
        self._migrate_module("module_080", "module_080_130", "8.0", "13.0")
        comparison = self._get_comparison("module_080", "module_080_130")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )

        log_content = _read_content(str(self._working_path / "test_log.log"))

        required_logs = [
            ("ERROR", "web_kanban_sparkline.*should remove the dependency"),
            ("WARNING", "Replaced.*account_analytic_analysis.*contract'"),
            ("ERROR", "deprecated decorator.*@api.cr"),
            ("ERROR", "ir.values.*removed"),
            ("ERROR", "removed module.*account_anglo_saxon"),
        ]

        for required_log in required_logs:
            level, message = required_log
            pattern = "{0}.*{1}".format(level, message)
            self.assertNotEqual(
                len(re.findall(pattern, log_content)),
                0,
                "%s not found in the log" % pattern,
            )

    def test_migration_120_130(self):
        self._migrate_module("module_120", "module_120_130", "12.0", "13.0")
        comparison = self._get_comparison("module_120", "module_120_130")
        diff_files = self._get_diff_files(comparison, "./")
        log_content = _read_content(str(self._working_path / "test_log.log"))
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )

        required_logs = [
            (
                "WARNING",
                "[13].*change.*env\\.user\\.company_id.*to.*\\.env\\.company",
            ),
        ]
        for required_log in required_logs:
            level, message = required_log
            pattern = "{0}.*{1}".format(level, message)
            self.assertNotEqual(
                len(re.findall(pattern, log_content)),
                0,
                "%s not found in the log" % pattern,
            )

    def test_migration_130_140(self):
        self._migrate_module("module_130", "module_130_140", "13.0", "14.0")
        comparison = self._get_comparison("module_130", "module_130_140")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )

    def test_migration_150_160(self):
        self._migrate_module("module_150", "module_150_160", "15.0", "16.0")
        comparison = self._get_comparison("module_150", "module_150_160")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )

    def test_migration_160_170(self):
        self._migrate_module("module_160", "module_160_170", "16.0", "17.0")
        comparison = self._get_comparison("module_160", "module_160_170")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )
        log_content = _read_content(str(self._working_path / "test_log.log"))
        required_logs = [
            (
                "WARNING",
                "[17].*'web.assets_common'.*This bundle has been removed.*",
            ),
        ]
        for required_log in required_logs:
            level, message = required_log
            pattern = "{0}.*{1}".format(level, message)
            self.assertNotEqual(
                len(re.findall(pattern, log_content)),
                0,
                "%s not found in the log" % pattern,
            )

    def test_migration_170_180(self):
        self._migrate_module("module_170", "module_170_180", "17.0", "18.0")
        comparison = self._get_comparison("module_170", "module_170_180")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )

    def test_migration_180_190(self):
        self._migrate_module("module_180", "module_180_190", "18.0", "19.0")
        comparison = self._get_comparison("module_180", "module_180_190")
        diff_files = self._get_diff_files(comparison, "./")
        self.assertEqual(
            len(diff_files),
            0,
            "Differences found in the following files\n- %s"
            % ("\n- ".join(diff_files)),
        )
