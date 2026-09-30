# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import csv
import io
import os
import re

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_OLD_ACCESS_FILE = "ir.model.access.csv"
_NEW_ACCESS_FILE = "ir.access.csv"
_NEW_ACCESS_HEADER = ["id", "name", "model_id", "group_id/id", "operation", "domain"]
# Odoo 20 spells the operations in this fixed order.
_PERM_COLUMNS = [
    ("c", "perm_create"),
    ("r", "perm_read"),
    ("u", "perm_write"),
    ("d", "perm_unlink"),
]
_MODEL_NAME_RE = re.compile(r"""^\s*_name\s*=\s*(['"])([\w.]+)\1""", re.MULTILINE)


def _models_by_table(module_path, tools):
    """Map table name -> model name for the models defined in the module."""
    res = {}
    for file in tools.get_files(module_path, (".py",)):
        for _quote, model in _MODEL_NAME_RE.findall(tools._read_content(file)):
            res[model.replace(".", "_")] = model
    return res


def _model_from_xmlid(xmlid, models_by_table, logger, file):
    """'module.model_res_partner' -> 'res.partner'.

    Without a database the table name is ambiguous when the model name has
    underscores, so models defined in the module are resolved first and the
    rest falls back to replacing '_' by '.' with a warning.
    """
    ref = xmlid.split(".")[-1]
    table = ref[len("model_") :] if ref.startswith("model_") else ref
    if table in models_by_table:
        return models_by_table[table]
    model = table.replace("_", ".")
    logger.warning(
        "[20] '%s' resolved to model '%s' by name only: check it in %s"
        % (xmlid, model, file)
    )
    return model


def migrate_ir_model_access_to_ir_access(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Convert security/ir.model.access.csv to the ir.access.csv of Odoo 20.

    Odoo ships odoo/upgrade_code/19.4-00-ir-access.py, which also folds the
    ir.rule records into the domain column, but it needs a database. This
    conversion only covers the CSV; ir.rule records are reported by text_errors.
    """
    models_by_table = _models_by_table(module_path, tools)
    for old_file in tools.get_files(module_path, (".csv",)):
        if old_file.name != _OLD_ACCESS_FILE:
            continue
        reader = csv.DictReader(io.StringIO(tools._read_content(old_file)))
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(_NEW_ACCESS_HEADER)
        for row in reader:
            model_xmlid = row.get("model_id:id") or row.get("model_id/id") or ""
            group_xmlid = row.get("group_id:id") or row.get("group_id/id") or ""
            operation = "".join(
                letter
                for letter, column in _PERM_COLUMNS
                if (row.get(column) or "0").strip() not in ("0", "", "False")
            )
            if not operation:
                logger.warning(
                    "[20] access '%s' grants no operation and will be dropped by"
                    " Odoo: check %s" % (row.get("id"), old_file)
                )
            writer.writerow(
                [
                    row.get("id", ""),
                    row.get("name", ""),
                    _model_from_xmlid(model_xmlid, models_by_table, logger, old_file),
                    group_xmlid,
                    operation,
                    "",
                ]
            )
        new_file = old_file.with_name(_NEW_ACCESS_FILE)
        tools._write_content(new_file, output.getvalue())
        os.remove(old_file)
        logger.info("Converted %s to %s" % (old_file, new_file))

    tools._replace_in_file(
        manifest_path,
        {re.escape(_OLD_ACCESS_FILE): _NEW_ACCESS_FILE},
        "Replace %s by %s in manifest" % (_OLD_ACCESS_FILE, _NEW_ACCESS_FILE),
    )


class MigrationScript(BaseMigrationScript):
    _GLOBAL_FUNCTIONS = [migrate_ir_model_access_to_ir_access]
