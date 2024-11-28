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


def replace_unaccent_parameter(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    files_to_process = tools.get_files(module_path, (".py",))
    replaces = {
        # Handle multiline with only unaccent=False
        r"(?s)fields\.(Char|Text|Html|Properties)\(\s*unaccent\s*=\s*False\s*,?\s*\)": r"fields.\1()",
        # Handle when unaccent=False is first parameter
        r"(?s)fields\.(Char|Text|Html|Properties)\(\s*unaccent\s*=\s*False\s*,\s*([^)]+?)\)": r"fields.\1(\2)",
        # Handle when unaccent=False is between other parameters
        r"(?s)fields\.(Char|Text|Html|Properties)\(([^)]+?),\s*unaccent\s*=\s*False\s*,\s*([^)]+?)\)": r"fields.\1(\2, \3)",
        # Handle when unaccent=False is the last parameter
        r"(?s)fields\.(Char|Text|Html|Properties)\(([^)]+?),\s*unaccent\s*=\s*False\s*\)": r"fields.\1(\2)",
    }

    for file in files_to_process:
        try:
            tools._replace_in_file(
                file,
                replaces,
                log_message=f"[18.0] Removed deprecated unaccent=False parameter in file: {file}",
            )
        except Exception as e:
            logger.error(f"Error processing file {file}: {str(e)}")


class MigrationScript(BaseMigrationScript):
    _GLOBAL_FUNCTIONS = [
        replace_unaccent_parameter,
        replace_tree_with_list_in_views,
        replace_chatter_blocks,
        replace_user_has_groups,
    ]
