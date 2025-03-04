# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import subprocess
import re
import pathlib
from lxml import etree
from dataclasses import fields

from .config import _AVAILABLE_MIGRATION_STEPS
from .log import logger


CLASS_PATTERN = re.compile(
    r"(class\s+\w+\s*\(\s*(?:\w+\.)?\w+(?:,\s*(?:\w+\.)?\w+)*\)\s*:\s*(?:\n\s+.*)+)",
    re.MULTILINE,
)


def _get_available_init_version_names():
    return [x["init_version_name"] for x in _AVAILABLE_MIGRATION_STEPS]


def _get_available_target_version_names():
    return [x["target_version_name"] for x in _AVAILABLE_MIGRATION_STEPS]


def _get_latest_version_name():
    return _AVAILABLE_MIGRATION_STEPS[-1]["target_version_name"]


def _get_latest_version_code():
    return _AVAILABLE_MIGRATION_STEPS[-1]["target_version_code"]


def _execute_shell(shell_command, path=False, raise_error=True):
    if path:
        shell_command = "cd '%s' && %s" % (str(path.resolve()), shell_command)
    logger.debug("Execute Shell:\n%s" % (shell_command))
    if raise_error:
        return subprocess.check_output(shell_command, shell=True)
    else:
        return subprocess.run(shell_command, shell=True)


def _read_content(file_path):
    f = open(file_path, "r")
    text = f.read()
    f.close()
    return text


def _write_content(file_path, content):
    f = open(file_path, "w")
    f.write(content)
    f.close()


def _replace_in_file(file_path, replaces, log_message=False):
    current_text = _read_content(file_path)
    new_text = current_text

    for old_term, new_term in replaces.items():
        new_text = re.sub(old_term, new_term or "", new_text)

    # Write file if changed
    if new_text != current_text:
        if not log_message:
            log_message = "Changing content of file: %s" % file_path.name
        logger.info(log_message)
        _write_content(file_path, new_text)
    return new_text


def _replace_field_names(file_path, replaces, log_message=False):
    current_text = _read_content(file_path)
    new_text = current_text
    # if the field is a python file with _inherit = model_name or <field name="name">model.name</field>
    # we try to replace the fields
    model = get_model(file_path)
    if model in replaces:
        model_field_name_replaces = replaces[model]
        # This replace is more careful on when and where we do replaces because the idea is to only change field
        # names instead of everywhere (i.e. changing move_type to type affects the arch type on xml files)
        if ".xml" in file_path:
            # replace only between inside the arch tags
            xml_data_bytes = new_text.encode("utf-8")
            root = etree.fromstring(xml_data_bytes)
            archs = root.xpath('.//field[@name="arch"]')
            # 3 looped for, not a good look
            for arch in archs:
                for tag in arch:
                    for old_term, new_term in model_field_name_replaces.items():
                        new_tag = etree.fromstring(
                            etree.tostring(tag).decode().replace(old_term, new_term)
                        )
                        arch.replace(tag, new_tag)
            new_text = etree.tostring(
                root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
            ).decode()
        elif ".py" in file_path:
            # replace only inside of classes
            for old_term, new_term in model_field_name_replaces.items():
                new_text = replace_in_classes(new_text, old_term, new_term)

    # Write file if changed
    if new_text != current_text:
        if not log_message:
            log_message = "Changing content of file: %s" % file_path.name
        logger.info(log_message)
        _write_content(file_path, new_text)
    return new_text


def get_files(module_path, extensions):
    """
    Returns a list of files with the specified extensions within the module_path.
    """
    file_paths = []
    module_dir = pathlib.Path(module_path)

    if not module_dir.is_dir():
        raise Exception(f"'{module_path}' is not a valid directory.")

    for ext in extensions:
        file_paths.extend(module_dir.rglob(f"*{ext}"))

    return file_paths


def get_model(absolute_filepath):
    model = ""
    match = ""
    with open(absolute_filepath, "r") as file:
        file_content = file.read()
        if "xml" in absolute_filepath:
            match = re.search(
                r"<field name=\"model\">([a-zA-Z0-9_.]+)</field>", file_content
            )
        elif "py" in absolute_filepath:
            match = re.search(r"_inherit\s*=\s*['\"]([^'\"]+)['\"]", file_content)
        if match:
            model = match.group(1)
    return model


def replace_in_classes(code, old_text, new_text):
    # Find all classes in the code
    classes = CLASS_PATTERN.findall(code)

    # Replace old_text with new_text in each class body
    for cls in classes:
        updated_class = cls.replace(old_text, new_text)
        code = code.replace(cls, updated_class)

    return code
