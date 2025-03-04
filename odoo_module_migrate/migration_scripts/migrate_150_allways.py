# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_module_migrate.base_migration_script import BaseMigrationScript


def replace_toggle_button(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".xml",))
    replaces = {
        r'widget="\s*toggle_button\s*"': 'widget="boolean_toggle"',
        r"widget='\s*toggle_button\s*'": 'widget="boolean_toggle"',
        r'<attribute\s+name=["\']widget["\']>\s*toggle_button\s*</attribute>': '<attribute name="widget">boolean_toggle</attribute>',
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"Replace toggle_button widget to boolean_toggle widget in file: {file}",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


class MigrationScript(BaseMigrationScript):
    _GLOBAL_FUNCTIONS = [replace_toggle_button]
