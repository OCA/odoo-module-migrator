# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import ast
import json
import re
from io import BytesIO

from lxml import etree

from odoo_module_migrate.base_migration_script import BaseMigrationScript


def migrate_expression_to_domain(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Convert odoo.osv.expression usage to odoo.fields.Domain"""
    files_to_process = tools.get_files(module_path, (".py",))

    for file in files_to_process:
        try:
            content = tools._read_content(file)
            original_content = content

            content = re.sub(
                r"from odoo\.osv import expression",
                "from odoo.fields import Domain",
                content,
            )

            content = re.sub(
                r"from odoo\.osv\.expression import (AND|OR|AND, OR|OR, AND)",
                "from odoo.fields import Domain",
                content,
            )

            content = re.sub(r"expression\.AND\(", "Domain.AND(", content)
            content = re.sub(r"expression\.OR\(", "Domain.OR(", content)

            content = re.sub(r"(?<!\.)AND\(", "Domain.AND(", content)
            content = re.sub(r"(?<!\.)OR\(", "Domain.OR(", content)

            content = re.sub(
                r"from odoo\.fields import Domain, (AND|OR|AND, OR|OR, AND)",
                "from odoo.fields import Domain",
                content,
            )

            lines = content.split("\n")
            seen_domain_import = False
            cleaned_lines = []

            for line in lines:
                if line.strip() == "from odoo.fields import Domain":
                    if not seen_domain_import:
                        cleaned_lines.append(line)
                        seen_domain_import = True
                else:
                    cleaned_lines.append(line)

            content = "\n".join(cleaned_lines)

            if content != original_content:
                tools._write_content(file, content)
                logger.info(f"Migrated expression imports to Domain in: {file}")

        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def upgrade_sql_constraints(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    # Odoo method in which we migrate all occurrences of _sql_constraints
    files_to_process = tools.get_files(module_path, (".py",))
    sql_expression_re = re.compile(r"\b_sql_constraints\s*=\s*\[([^\]]+)]")
    ind = " " * 4

    # Function to build the new SQL constraint definition
    def build_sql_object(match):
        constraints = ast.literal_eval("[" + match.group(1) + "]")
        result = []
        for name, definition, *messages in constraints:
            message = messages[0] if messages else ""
            constructor = "Constraint"
            if message:
                # format on 2 lines
                message_repr = json.dumps(
                    message, ensure_ascii=False
                )  # so that the message is in double quotes
                args = f"\n{ind * 2}{definition!r},\n{ind * 2}{message_repr},\n{ind}"
            elif len(definition) > 60:
                args = f"\n{ind * 2}{definition!r}"
            else:
                args = repr(definition)
            result.append(f"_{name} = models.{constructor}({args})")
        return f"\n{ind}".join(result)

    # Process each file
    for file in files_to_process:
        content = tools._read_content(file)
        content = sql_expression_re.sub(build_sql_object, content)
        if sql_expression_re.search(content):
            logger.warning("Failed to replace sql_constraints")
        tools._write_content(file, content)


def _remove_group_attrs_in_search_views(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Remove `expand` and `string` attributes from <group> tags when they
    are inside a <search> view.
    """

    files_to_process = tools.get_files(module_path, (".xml",))

    for file_path in files_to_process:
        try:
            content = tools._read_content(file_path)
            parser = etree.XMLParser(recover=True)
            try:
                # lxml does not accept unicode strings with XML declaration,
                # so parse from bytes to be safe.
                tree = etree.parse(BytesIO(content.encode("utf-8")), parser)
                root = tree.getroot()
            except Exception:
                # If full-parse fails, skip this file
                continue

            changed = False

            # Find all <search> elements and remove expand/string from <group> children
            for search in root.findall(".//search"):
                for group in search.findall(".//group"):
                    for attr in ("expand", "string"):
                        if attr in group.attrib:
                            del group.attrib[attr]
                            changed = True

            if changed:
                # Write back modified tree
                new_content = etree.tostring(
                    root, encoding="utf-8", xml_declaration=True
                ).decode("utf-8")
                new_content = new_content.replace(
                    "<?xml version='1.0' encoding='utf-8'?>",
                    '<?xml version="1.0" encoding="utf-8"?>',
                )
                if not new_content.endswith("\n"):
                    new_content += "\n"
                tools._write_content(file_path, new_content)
                logger.info(
                    f"Removed expand/string attrs from <group> in search views: {file_path}"
                )

        except Exception as e:
            logger.error(f"Error processing XML file {file_path}: {e}")


class MigrationScript(BaseMigrationScript):
    _GLOBAL_FUNCTIONS = [
        upgrade_sql_constraints,
        migrate_expression_to_domain,
        _remove_group_attrs_in_search_views,
    ]
