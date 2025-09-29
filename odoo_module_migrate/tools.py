# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import subprocess
import re
import pathlib
import ast

from .config import _AVAILABLE_MIGRATION_STEPS
from .log import logger


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


def read_lines(file_path):
    content = _read_content(file_path)
    lines = content.splitlines()
    return enumerate(lines)


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


class OdooClassAnalyzer:
    def __init__(self, file_path):
        with open(file_path, "r") as f:
            self.content = f.read()

        tree = ast.parse(self.content)
        self.classes = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                _name = None
                _inherit = []

                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == "_name" and isinstance(
                                    item.value, ast.Constant
                                ):
                                    _name = item.value.value
                                elif target.id == "_inherit":
                                    if isinstance(item.value, ast.Constant):
                                        _inherit = [item.value.value]
                                    elif isinstance(item.value, ast.List):
                                        _inherit = [
                                            elt.value
                                            for elt in item.value.elts
                                            if isinstance(elt, ast.Constant)
                                        ]

                if _name:
                    loops = self._find_loops_in_class(node)
                    self.classes[_name] = {
                        "class_name": class_name,
                        "_name": _name,
                        "_inherit": _inherit,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "loops": loops,
                    }

    def _find_loops_in_class(self, class_node):
        """
        Find 'for variable in self:' loops in the class definition.
        Returns a dictionary with variable names as keys and their start and end lines.
        """
        loops = {}
        start_line = class_node.lineno
        end_line = class_node.end_lineno
        class_lines = self.content.split("\n")[start_line - 1 : end_line]

        for i, line in enumerate(class_lines):
            match = re.search(r"^(\s*)for\s+([a-zA-Z_]\w*)\s+in\s+self\s*:", line)
            if match:
                indentation = len(match.group(1))
                variable_name = match.group(2)
                loop_start_relative = i

                loop_end_relative = len(class_lines) - 1
                for j in range(i + 1, len(class_lines)):
                    current_line = class_lines[j]
                    if current_line.strip() == "":
                        continue

                    current_indentation = len(current_line) - len(current_line.lstrip())
                    if current_indentation <= indentation:
                        loop_end_relative = j - 1
                        break

                loops[variable_name] = {
                    "start_line_relative": loop_start_relative,
                    "end_line_relative": loop_end_relative,
                }

        return loops

    def has_model(self, model_name):
        for value in self.classes.values():
            if model_name == value["_name"] or model_name in value["_inherit"]:
                return True
        return False

    def get_model_info(self, model_name):
        for value in self.classes.values():
            if model_name == value["_name"] or model_name in value["_inherit"]:
                return value
        return False


def analyze_field_changes(
    file_path, field_replacements, field_removals, warnings_by_message
):
    """
    Analyzes a Python file to find and replace field names in Odoo model definitions.
    Handles 'self.<field>' and 'for variable in self:' loops.
    """
    analyzer = OdooClassAnalyzer(file_path)
    content = _read_content(file_path)

    base_patterns = [
        (r"\b{variable}\.{old_field}\b", r"{variable}.{new_field}"),
        (
            r'({variable}\.(write|create)\s*\([^}}]*?)(["\']){old_field}\3',
            r'\1"{new_field}"',
        ),
    ]
    total_replacements = 0
    for model_name, old_field, new_field, _ in field_replacements:
        if analyzer.has_model(model_name):
            model_info = analyzer.get_model_info(model_name)
            start_line = model_info["start_line"]
            end_line = model_info["end_line"]
            loops = model_info["loops"]

            lines = content.split("\n")
            model_lines = lines[start_line - 1 : end_line]
            model_content = "\n".join(model_lines)
            original_model_content = model_content

            count = 0
            for pattern, replace in base_patterns:
                pattern_formatted = pattern.format(
                    variable="self", old_field=re.escape(old_field)
                )
                replace_formatted = replace.format(variable="self", new_field=new_field)
                matches = re.findall(
                    pattern_formatted, original_model_content, flags=re.DOTALL
                )
                count += len(matches)
                model_content = re.sub(
                    pattern_formatted, replace_formatted, model_content, flags=re.DOTALL
                )

            model_lines_modified = model_content.split("\n")
            for variable_name, loop_info in loops.items():
                loop_start = loop_info["start_line_relative"] + 1
                loop_end = loop_info["end_line_relative"] + 1

                loop_lines = model_lines_modified[loop_start:loop_end]
                loop_content = "\n".join(loop_lines)
                original_loop_content = loop_content

                for pattern, replace in base_patterns:
                    pattern = pattern.format(
                        variable=re.escape(variable_name),
                        old_field=re.escape(old_field),
                    )
                    replace = replace.format(
                        variable=variable_name, new_field=new_field
                    )
                    matches = re.findall(
                        pattern, original_loop_content, flags=re.DOTALL
                    )
                    count += len(matches)
                    loop_content = re.sub(
                        pattern, replace, loop_content, flags=re.DOTALL
                    )

                model_lines_modified[loop_start:loop_end] = loop_content.split("\n")

            model_content_final = "\n".join(model_lines_modified)
            if count > 0:
                lines[start_line - 1 : end_line] = model_content_final.split("\n")
                content = "\n".join(lines)
                total_replacements += count
                logger.info(
                    f"{model_name}: {old_field} -> {new_field} ({count} changes)"
                )

    _write_content(file_path, content)

    for model_name, field_name, more_info in field_removals:
        if analyzer.has_model(model_name):
            model_info = analyzer.get_model_info(model_name)
            lines = content.split("\n")
            model_content = "\n".join(
                lines[model_info["start_line"] - 1 : model_info["end_line"]]
            )

            for pattern, _ in base_patterns:
                pattern_formatted = pattern.format(old_field=re.escape(field_name))
                if re.search(pattern_formatted, model_content, flags=re.DOTALL):
                    msg = f"Field '{field_name}' of model '{model_name}' was removed. {more_info or ''}"
                    warnings_by_message.setdefault(msg, set()).add(str(file_path))
