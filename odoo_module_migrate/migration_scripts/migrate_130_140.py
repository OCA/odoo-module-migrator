# Copyright (C) 2020 - Today: Iván Todorovich
# Copyright (C) 2020 - Today: Simone Rubino
# @author: Iván Todorovich (https://twitter.com/ivantodorovich)
# @author: Simone Rubino (https://github.com/Daemo00)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re
from pathlib import Path
import lxml.etree as et
from odoo_module_migrate.base_migration_script import BaseMigrationScript


def src_model_new_value(field_elem, model_dot_name):
    """
    Particular behavior for new binding_model_id.

    Apply some heuristic to change
    old attribute `src_model=account.move`
    to `<field name="binding_model_id" ref="account.model_account_move"/>`.
    """
    module_name = model_dot_name.split(".")[0]
    model_und_name = model_dot_name.replace(".", "_")
    ref_value = f"{module_name}.model_{model_und_name}"
    field_elem.set("ref", ref_value)


def value_to_text(field_elem, attr_value):
    """Standard behavior: an attribute value is the new fields's text."""
    field_elem.text = attr_value


TAG_ATTR_RENAMING = {
    "report": {
        "name": ("report_name", value_to_text),
        "string": ("name", value_to_text),
    },
    "act_window": {
        "src_model": ("binding_model_id", src_model_new_value),
    },
}
"""
Configuration for renaming particular attributes.

The dictionary maps old tag names to their attributes' names.
Each old attribute name is then mapped a tuple containing:

- name of the corresponding new field
- a function that applies the old attribute's value to the new field
"""


def _reformat_file(file_path: Path):
    """Reformat `file_path`.

    Substitute `act_window` and `report` tag with `record` tag.
    Note that:
    - `id` attribute is kept in the `record` tag;
    - in `report` tag:
      - `string` has been renamed to `name`;
      - `name` has been renamed to `report_name`;
    - other attributes are assigned to respective fields
    """
    parser = et.XMLParser(remove_blank_text=True)
    tree = et.parse(str(file_path.resolve()), parser)
    root = tree.getroot()
    reformat_tags = (*root.findall("act_window"), *root.findall("report"))
    if not reformat_tags:
        return None

    regexp = r"(?P<indent>[ \t]*)" r"(?P<tag><{tag_type}[^/]*id=\"{tag_id}\"[^/]*/>)"

    new_tags_dict = dict()
    for tag in reformat_tags:
        tag_regex = regexp.format(
            tag_type=tag.tag,
            tag_id=tag.attrib["id"],
        )
        for attrib, value in tag.attrib.items():
            if attrib == "id":
                continue
            tag.attrib.pop(attrib)

            attr_renames_dict = TAG_ATTR_RENAMING.get(tag.tag, dict())
            new_value_func = value_to_text
            if attrib in attr_renames_dict:
                new_attr_name, new_value_func = attr_renames_dict.get(attrib)
                attrib = new_attr_name

            field_elem = et.SubElement(tag, "field", {"name": attrib})
            new_value_func(field_elem, value)

        tag.attrib["model"] = "ir.actions." + tag.tag
        tag.tag = "record"

        new_tags_dict[tag_regex] = tag

    # Read in the file
    xml_file = file_path.read_text()

    # Replace the target string
    for tag_regex, tag in new_tags_dict.items():
        match = re.search(tag_regex, xml_file)
        if match:
            indent = match.group("indent")
            tag_match = match.group("tag")
            et.indent(tag, space=indent, level=1)
            # Remove trailing newline
            tag_string = et.tostring(tag, pretty_print=True)[:-1]
            xml_file = re.sub(tag_match, tag_string.decode(), xml_file)

    # Write the file out again
    file_path.write_text(xml_file)
    return file_path


def _get_files(module_path, reformat_file_ext):
    """Get files to be reformatted."""
    file_paths = list()
    if not module_path.is_dir():
        raise Exception(f"'{module_path}' is not a directory")
    file_paths.extend(module_path.rglob("*" + reformat_file_ext))
    return file_paths


def reformat_deprecated_tags(
    logger, module_path, module_name, manifest_path, migration_steps, tools
):
    """Reformat deprecated tags in XML files.

    Deprecated tags are `act_window` and `report`:
    they have to be substituted by the `record` tag.
    """

    reformat_file_ext = ".xml"
    file_paths = _get_files(module_path, reformat_file_ext)
    logger.debug(f"{reformat_file_ext} files found:\n" f"{list(map(str, file_paths))}")

    reformatted_files = list()
    for file_path in file_paths:
        reformatted_file = _reformat_file(file_path)
        if reformatted_file:
            reformatted_files.append(reformatted_file)
    logger.debug("Reformatted files:\n" f"{list(reformatted_files)}")


def refactor_action_read(**kwargs):
    """
    replace action.read() by _for_xml_id to avoid access rights issue

    ##### case 1: pattern for case action.read[0] right after self.env.ref
    ## action = self.env.ref('sale.action_orders')
    ## action = action.read()[0]

    ##### case 2: pattern for case having new line between action.read[0] and self.env.ref
    ## action = self.env.ref('sale.action_orders')
    ## .........
    ## .........
    ## action = action.read()[0]
    """
    logger = kwargs["logger"]
    tools = kwargs["tools"]
    module_path = kwargs["module_path"]
    file_paths = _get_files(module_path, ".py")

    old_term = r"action.*= self.env.ref\((.*)\)((\n.+)+?)?(\n.+)(action\.read\(\)\[0\])"
    new_term = r'\2\4self.env["ir.actions.act_window"]._for_xml_id(\1)'
    for file_path in file_paths:
        logger.debug(f"refactor file {file_path}")
        tools._replace_in_file(
            file_path,
            {old_term: new_term},
            log_message="refactor action.read[0] to _for_xml_id",
        )


_TEXT_REPLACES = {
    ".js": {
        r"tour\.STEPS\.SHOW_APPS_MENU_ITEM": "tour.stepUtils.showAppsMenuItem()",
        r"tour\.STEPS\.TOGGLE_HOME_MENU": "tour.stepUtils.toggleHomeMenu()",
    },
    ".py": {
        r"\.phantom_js\(": ".browser_js(",
    },
}


class MigrationScript(BaseMigrationScript):

    _GLOBAL_FUNCTIONS = [reformat_deprecated_tags, refactor_action_read]
    _TEXT_REPLACES = _TEXT_REPLACES
