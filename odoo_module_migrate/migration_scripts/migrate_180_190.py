# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

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

    _GLOBAL_FUNCTIONS = [upgrade_sql_constraints]
