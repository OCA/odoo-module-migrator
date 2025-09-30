# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo_module_migrate.base_migration_script import BaseMigrationScript
import re


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


import ast
import json
import re


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


class MigrationScript(BaseMigrationScript):

    _GLOBAL_FUNCTIONS = [
        upgrade_sql_constraints,
        migrate_expression_to_domain,
    ]
