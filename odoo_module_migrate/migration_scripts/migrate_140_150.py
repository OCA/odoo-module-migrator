# Copyright (C) 2024 - Today: NextERP Romania (https://nexterp.ro)
# @author: Mihai Fekete (https://github.com/NextERP-Romania)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast
import json
import lxml.etree as et
import os

from odoo_module_migrate.base_migration_script import BaseMigrationScript


def add_asset_to_manifest(assets, manifest):
    """Add an asset to a manifest file."""
    if "assets" not in manifest:
        manifest["assets"] = {}
    for asset_type, asset_files in assets.items():
        if asset_type not in manifest["assets"]:
            manifest["assets"][asset_type] = []
        manifest["assets"][asset_type].extend(asset_files)


def remove_asset_file_from_manifest(file, manifest):
    """Remove asset file from manifest views."""
    if "data" not in manifest:
        return
    for file_path in manifest["data"]:
        if file_path == file:
            manifest["data"].remove(file)


def remove_node_from_xml(record_node, node):
    """Remove a node from an XML tree."""
    to_remove = True
    if node.getchildren():
        to_remove = False
    if to_remove:
        parent = node.getparent() if node.getparent() is not None else record_node
        parent.remove(node)


def reformat_assets_definition(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Reformat assets declaration in XML files."""

    manifest = tools._get_manifest_dict(manifest_path)
    parser = et.XMLParser(remove_blank_text=True)
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
        "web_enterprise.assets_backend",
        "web_enterprise.assets_common",
        "web_enterprise._assets_backend_helpers",
    ]
    for file_path in manifest.get("data", []):
        if not file_path.endswith(".xml"):
            continue
        xml_file = open(os.path.join(module_path, file_path), "r")
        tree = et.parse(xml_file, parser)
        record_node = tree.getroot()
        for node in record_node.getchildren():
            if node.get("inherit_id") in assets_views:
                for xpath_elem in node.xpath("xpath[@expr]"):
                    for file in xpath_elem.getchildren():
                        elem_file_path = False
                        if file.get("src"):
                            elem_file_path = ["".join(file.get("src"))]
                        elif file.get("href"):
                            elem_file_path = ["".join(file.get("href"))]
                        if elem_file_path:
                            add_asset_to_manifest(
                                {node.get("inherit_id"): elem_file_path},
                                manifest,
                            )
                            remove_node_from_xml(record_node, file)
                    remove_node_from_xml(record_node, xpath_elem)
            remove_node_from_xml(record_node, node)
        # write back the node to the XML file
        with open(os.path.join(module_path, file_path), "wb") as f:
            et.indent(tree)
            tree.write(f, encoding="utf-8", xml_declaration=True)
        if not record_node.getchildren():
            remove_asset_file_from_manifest(file_path, manifest)
            os.remove(os.path.join(module_path, file_path))
    manifest_content = json.dumps(manifest, indent=4, default=str)
    manifest_content = manifest_content.replace(": true", ": True").replace(
        ": false", ": False"
    )
    tools._write_content(manifest_path, manifest_content)


class MigrationScript(BaseMigrationScript):

    _GLOBAL_FUNCTIONS = [reformat_assets_definition]
