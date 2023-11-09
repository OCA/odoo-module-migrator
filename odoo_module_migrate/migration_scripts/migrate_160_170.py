# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_module_migrate.base_migration_script import BaseMigrationScript
import lxml.etree as et
from pathlib import Path


def _get_files(module_path, reformat_file_ext):
    """Get files to be reformatted."""
    file_paths = list()
    if not module_path.is_dir():
        raise Exception(f"'{module_path}' is not a directory")
    file_paths.extend(module_path.rglob("*" + reformat_file_ext))
    return file_paths


def _check_open_form_view(logger, file_path: Path):
    """Check if the view has a button to open a form reg in a tree view `file_path`."""
    parser = et.XMLParser(remove_blank_text=True)
    tree = et.parse(str(file_path.resolve()), parser)
    record_node = tree.getroot()[0]
    f_arch = record_node.find('field[@name="arch"]')
    root = f_arch if f_arch is not None else record_node
    for button in root.findall(".//button[@name='get_formview_action']"):
        logger.warning(
            (
                "Button to open a form reg form a tree view detected in file %s line %s, probably should be changed by open_form_view='True'. More info here https://github.com/odoo/odoo/commit/258e6a019a21042bf4f6cf70fcce386d37afd50c"
            )
            % (file_path.name, button.sourceline)
        )


def _check_open_form(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    reformat_file_ext = ".xml"
    file_paths = _get_files(module_path, reformat_file_ext)
    logger.debug(f"{reformat_file_ext} files found:\n" f"{list(map(str, file_paths))}")

    for file_path in file_paths:
        _check_open_form_view(logger, file_path)


class MigrationScript(BaseMigrationScript):

    _GLOBAL_FUNCTIONS = [_check_open_form]
