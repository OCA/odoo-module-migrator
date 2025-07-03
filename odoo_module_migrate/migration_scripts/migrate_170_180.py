# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# This script is based on the original code from:
# https://github.com/odoo/odoo/blob/master/odoo/upgrade_code/17.5-00-tree-to-list.py

from odoo_module_migrate.base_migration_script import BaseMigrationScript
import re


def replace_tree_with_list_in_views(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".xml", ".js", ".py"))

    reg_tree_to_list_xml_mode = re.compile(
        r"""(<field[^>]* name=["'](view_mode|name|binding_view_types)["'][^>]*>([^<>]+[,.])?\s*)tree(\s*([,.][^<>]+)?</field>)"""
    )
    reg_tree_to_list_tag = re.compile(r"([<,/])tree([ \n\r,>/])")
    reg_tree_to_list_xpath = re.compile(
        r"""(<xpath[^>]* expr=['"])([^<>]*/)?tree(/|[\['"])"""
    )
    reg_tree_to_list_ref = re.compile(r"tree_view_ref")
    reg_tree_to_list_mode = re.compile(r"""(mode=['"][^'"]*)tree([^'"]*['"])""")
    reg_tree_to_list_view_mode = re.compile(
        r"""(['"]view_mode['"][^'":=]*[:=].*['"]([^'"]+,)?\s*)tree(\s*(,[^'"]+)?['"])"""
    )
    reg_tree_to_list_view = re.compile(
        r"""(['"]views['"][^'":]*[:=].*['"])tree(['"])"""
    )
    reg_tree_to_list_string = re.compile(r"""([ '">)])tree( [vV]iews?[ '"<.)])""")
    reg_tree_to_list_String = re.compile(r"""([ '">)])Tree( [vV]iews?[ '"<.)])""")
    reg_tree_to_list_env_ref = re.compile(r"""(self\.env\.ref\(.*['"])tree(['"])""")

    for file in files_to_process:
        try:
            content = tools._read_content(file)
            content = content.replace(" tree view ", " list view ")
            content = reg_tree_to_list_xml_mode.sub(r"\1list\4", content)
            content = reg_tree_to_list_tag.sub(r"\1list\2", content)
            content = reg_tree_to_list_xpath.sub(r"\1\2list\3", content)
            content = reg_tree_to_list_ref.sub("list_view_ref", content)
            content = reg_tree_to_list_mode.sub(r"\1list\2", content)
            content = reg_tree_to_list_view_mode.sub(r"\1list\3", content)
            content = reg_tree_to_list_view.sub(r"\1list\2", content)
            content = reg_tree_to_list_string.sub(r"\1list\2", content)
            content = reg_tree_to_list_String.sub(r"\1List\2", content)
            content = reg_tree_to_list_env_ref.sub(r"\1list\2", content)

            tools._write_content(file, content)

        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def replace_chatter_blocks(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".xml",))

    reg_chatter_block = r"""<div class=["']oe_chatter["'](?![^>]*position=["'][^"']+["'])[^>]*>[\s\S]*?</div>"""
    reg_xpath_chatter = r"""//div\[hasclass\(['"]oe_chatter['"]\)\]"""
    reg_chatter_with_position_self_closing = (
        r"""<div class=["']oe_chatter["']\s*(position=["'][^"']+["'])\s*/>"""
    )

    replacement_div = "<chatter/>"
    replacement_xpath = "//chatter"

    def replace_chatter_self_closing(match):
        position = match.group(1)
        return f"<chatter {position}/>"

    replaces = {
        reg_chatter_block: replacement_div,
        reg_xpath_chatter: replacement_xpath,
        reg_chatter_with_position_self_closing: replace_chatter_self_closing,
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file, replaces, log_message=f"Updated chatter blocks in file: {file}"
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def replace_user_has_groups(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".py",))
    replaces = {
        r"self\.user_has_groups\(\s*(['\"])([\w\.]+)\1\s*\)": r"self.env.user.has_group(\1\2\1)",
        r"self\.user_has_groups\(\s*(['\"])([^'\"]*[,!][^'\"]*?)\1\s*\)": r"self.env.user.has_groups(\1\2\1)",
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(file, replaces)
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def remove_deprecated_kanban_click_classes(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".xml",))

    replaces = {
        "oe_kanban_global_click_edit": "",
        "oe_kanban_global_click": "",
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"Remove deprecated kanban click classes in file: {file}",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def replace_kanban_color_picker_widget(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".xml",))

    replaces = {
        # Case 1: Match any ul tag containing both oe_kanban_colorpicker class and data-field
        # Example: <ul class="oe_kanban_colorpicker some-class" data-field="color" some-attr="value"/>
        # Example: <ul data-field="color" t-if="condition" class="oe_kanban_colorpicker other-class"/>
        r'<ul[^>]*?class="[^"]*?oe_kanban_colorpicker[^"]*?"[^>]*?data-field="([^"]+)"[^>]*?>(?:</ul>)?': r'<field name="\1" widget="kanban_color_picker"/>',
        # Case 2: Same as Case 1 but with data-field appearing before class
        # Example: <ul data-field="color" class="some-class oe_kanban_colorpicker" some-attr="value"/>
        # Example: <ul some-attr="value" data-field="color" class="oe_kanban_colorpicker"/>
        r'<ul[^>]*?data-field="([^"]+)"[^>]*?class="[^"]*?oe_kanban_colorpicker[^"]*?"[^>]*?>(?:</ul>)?': r'<field name="\1" widget="kanban_color_picker"/>',
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"Replace kanban colorpicker with field widget in file: {file}",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def remove_kanban_tooltip(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".xml",))
    reg_tooltip_template = (
        r"""<t\s+t-name=["']kanban-tooltip["'][^>]*>[\s\S]*?</t>\s*"""
    )
    reg_tooltip_attr = r"""\s+tooltip=["']kanban-tooltip["']"""

    replaces = {
        reg_tooltip_template: "",
        reg_tooltip_attr: "",
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"Removed kanban tooltip feature in file: {file}",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


def replace_type_edit(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Replace type='edit' with type='open' in elements."""
    files_to_process = tools.get_files(module_path, (".xml",))

    reg_type_edit = r"""type=["']edit["']"""

    replaces = {
        reg_type_edit: 'type="open"',
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"Replaced type='edit' with type='open' in file: {file}",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


class MigrationScript(BaseMigrationScript):
    _GLOBAL_FUNCTIONS = [
        remove_deprecated_kanban_click_classes,
        replace_kanban_color_picker_widget,
        remove_kanban_tooltip,
        replace_type_edit,
        replace_tree_with_list_in_views,
        replace_chatter_blocks,
        replace_user_has_groups,
    ]
