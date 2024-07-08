# Copyright (C) 2024 - Today: NextERP Romania (https://nexterp.ro)
# @author: Mihai Fekete (https://github.com/NextERP-Romania)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
import lxml

from pathlib import Path
from odoo_module_migrate.base_migration_script import BaseMigrationScript


def add_asset_to_manifest(assets, manifest):
    """Add an asset to a manifest file."""
    if "assets" not in manifest:
        manifest["assets"] = {}
    for asset_type, asset_files in assets.items():
        if asset_type not in manifest["assets"]:
            manifest["assets"][asset_type] = []
        manifest["assets"][asset_type].extend(asset_files)


def remove_asset_file_from_manifest(cr, logger, file, manifest):
    """Remove asset file from manifest views."""
    if "data" not in manifest:
        return
    for file in manifest["data"]:
        if file == file:
            manifest["data"].remove(file)


def reformat_assets_definition(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Reformat assets declaration in XML files."""

    manifest = {}
    import ipdb

    ipdb.set_trace()
    f = open(manifest_path, "r")
    text = f.read()
    manifest = lxml.etree.parse(text)
    current_manifest_text = tools._read_content(manifest_path)
    assets_views = [
        "web.assets_backend",
        "web.assets_common",
        "web.assets_frontend",
        "web.assets_qweb",
        "web.assets_tests",
        "website.assets_frontend",
        "website.assets_editor",
        "website.assets_frontend_editor",
        "website.assets_wysiwyg",
    ]
    for f in manifest.get("data", []):
        if not f.endswith(".xml"):
            continue
        f = open(os.path.join(module, f), "r")
        text = f.read()
        doc = lxml.etree.parse(fp)
        for node in doc.xpath(xpath):
            if node.get("inherit_id") in assets_views:
                for line in node.xpath("xpath[@expr]"):
                    if line.get("src"):
                        add_asset_to_manifest(
                            {node.get("inherit_id"): line.get("src")},
                            manifest,
                        )
                        node.remove(line)


class MigrationScript(BaseMigrationScript):

    _GLOBAL_FUNCTIONS = [reformat_assets_definition]
