# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re
from odoo_module_migrate.base_migration_script import BaseMigrationScript


def multi_value_translation_replacement_function(match, single_quote=True):
    format_string = match.group(1)
    dictionary_entries = match.group(2)

    formatted_entries = []
    for entry in dictionary_entries.split(","):
        if ":" in entry:
            [key, value] = entry.split(":")
            formatted_entries.append(
                "{}={}".format(key.strip().strip("'").strip('"'), value.strip())
            )

    formatted_entries = ", ".join(formatted_entries)

    if single_quote:
        return f"_('{format_string}', {formatted_entries})"
    return f'_("{format_string}", {formatted_entries})'


def format_parenthesis(match):
    format_string = match.group(1)
    dictionary_entries = match.group(2)

    if dictionary_entries.endswith(","):
        dictionary_entries = dictionary_entries[:-1]

    return f"_({format_string}, {dictionary_entries})"


def format_replacement_function(match, single_quote=True):
    format_string = re.sub(r"\{\d*\}", "%s", match.group(1))
    format_string = re.sub(r"{(\w+)}", r"%(\1)s", format_string)
    arguments = " ".join(match.group(2).split())

    if arguments.endswith(","):
        arguments = arguments[:-1]

    if single_quote:
        return f"_('{format_string}', {arguments})"
    return f'_("{format_string}", {arguments})'


def replace_translation_function(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".py",))

    replaces = {
        r'_\(\s*"([^"]+)"\s*\)\s*%\s*\{([^}]+)\}': lambda match: multi_value_translation_replacement_function(
            match, single_quote=False
        ),
        r"_\(\s*'([^']+)'\s*\)\s*%\s*\{([^}]+)\}": lambda match: multi_value_translation_replacement_function(
            match, single_quote=True
        ),
        r'_\((["\'].*?%[ds].*?["\'])\)\s*%\s*\(\s*(.+)\s*\)': format_parenthesis,
        r'_\((["\'].*?%[ds].*?["\'])\)\s*?%\s*?([^\s]+)': r"_(\1, \2)",
        r'_\(\s*"([^"]*)"\s*\)\.format\(\s*(\s*[^)]+)\)': lambda match: format_replacement_function(
            match, single_quote=False
        ),
        r"_\(\s*'([^']*)'\s*\)\.format\(\s*(\s*[^)]+)\)": lambda match: format_replacement_function(
            match, single_quote=True
        ),
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"""Improve _() function: {file}""",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


class MigrationScript(BaseMigrationScript):

    _GLOBAL_FUNCTIONS = [replace_translation_function]
