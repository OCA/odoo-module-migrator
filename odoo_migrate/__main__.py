# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import argcomplete
import logging
import importlib
import os
import re
from pathlib import Path
from . import migrate_tools


_logger = logging.getLogger(__name__)

_ALLOWED_EXTENSIONS = [".py", ".xml", ".js"]

_MIGRATION_LIST = [
    ("8.0", "9.0"),
    ("9.0", "10.0"),
    ("10.0", "11.0"),
    ("11.0", "12.0"),
]


def _migrate_module(args, module_path):
    migration_list = _get_migration_list(
        args.init_version, args.target_version
    )

    for migration in migration_list:
        # Execute specific migration for a version to another
        # Exemple 8.0 -> 9.0
        script_module = importlib.import_module(
            "odoo_migrate.migrate_%s__%s"
            % (
                migration[0].replace(".", "_"),
                (migration[1].replace(".", "_")),
            )
        )
        _migrate_module_script(
            args, module_path, script_module
        )

        # Execute migration that have to be done for all version after
        # a given revision
        # Exemple remove python3 header if version >= to 11.0
        script_module = importlib.import_module(
            "odoo_migrate.migrate_%s__all" % (migration[0].replace(".", "_"))
        )
        _migrate_module_script(
            args, module_path, script_module
        )

    # Finally, execute a script that will be allways executed
    script_module = importlib.import_module("odoo_migrate.migrate_allways")
    _migrate_module_script(args, module_path, script_module)


def _migrate_module_script(
        args, module_path, script_module):
    _logger.debug(
        "Begin migration script '%s' in folder %s "
        % (script_module.__name__, module_path)
    )

    file_renames = getattr(script_module, "_FILE_RENAMES", {})
    # text_replaces = getattr(script_module, "_TEXT_REPLACES", {})
    text_warnings = getattr(script_module, "_TEXT_WARNING", {})

    for root, directories, filenames in os.walk(module_path._str):
        for filename in filenames:
            # Skip useless file
            # TODO, skip files present in some folders. (for exemple 'lib')
            extension = os.path.splitext(filename)[1]
            if extension not in _ALLOWED_EXTENSIONS:
                continue

            filenameWithPath = os.path.join(root, filename)
            _logger.debug("Migrate '%s' file" % filenameWithPath)

            # Rename file, if required
            new_name = file_renames.get(filename)
            if new_name:
                migrate_tools._rename_file(
                    _logger, module_path, filenameWithPath,
                    os.path.join(root, new_name))
                filenameWithPath = os.path.join(root, new_name)

            # Operate changes in the file (replacement, changes)
            with open(filenameWithPath, "U") as f:
                currentText = f.read()
                newText = currentText

            #     replaces = text_replaces.get("*", {})
            #     replaces.update(text_replaces.get(extension, {}))

            #     for old_term, new_term in replaces.items():
            #         newText = re.sub(old_term, new_term, newText)

            #     # Write file if changed
            #     if newText != currentText:
            #         _logger.info("Changing content of file: %s" % filename)
            #         with open(filenameWithPath, "w") as f:
            #             f.write(newText)

                # Display warnings if the file content some obsolete code
                warnings = text_warnings.get("*", {})
                warnings.update(text_warnings.get(extension, {}))
                for pattern, warning_message in warnings.items():
                    if re.findall(pattern, newText):
                        _logger.warning(warning_message)


def _get_init_versions():
    return [x[0] for x in _MIGRATION_LIST]


def _get_target_versions():
    return [x[1] for x in _MIGRATION_LIST]


def _get_latest_version():
    return _MIGRATION_LIST[-1][1]


def _get_migration_list(init_version, target_version):
    found = False
    res = []
    for item in _MIGRATION_LIST:
        if not found and item[0] != init_version:
            continue
        else:
            found = True
        res.append(item)
        if item[1] == target_version:
            return res


def get_parser():
    """Return :py:class:`argparse.ArgumentParser` instance for CLI."""

    main_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )

    main_parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        required=True,
        type=str,
        help="Target Modules directory. Set here a folder path"
        " that contains Odoo modules you want to migrate from a version"
        " to another.",
    )

    main_parser.add_argument(
        "-m",
        "--module_list",
        dest="module_list",
        type=str,
        help="Targer Modules to migrate."
        " If not set, all the modules present in the directory will be"
        " migrated.",
    )

    main_parser.add_argument(
        "-i",
        "--init-version",
        choices=_get_init_versions(),
        dest="init_version",
        required=True,
        type=str,
    )

    main_parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        dest="log_level",
        default="INFO",
        type=str,
    )

    main_parser.add_argument(
        "-t",
        "--target-version",
        dest="target_version",
        type=str,
        choices=_get_target_versions(),
        default=_get_latest_version(),
        help="Target version of the Odoo module you want to migrate."
        " If 'latest' is set, the tool will try to migrate to the latest"
        " Odoo version.",
    )

    return main_parser


def main():
    # Parse Arguments
    parser = get_parser()
    argcomplete.autocomplete(parser, always_complete_options=False)
    args = parser.parse_args()

    # Set log level
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)-10s %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(getattr(logging, str(args.log_level)))

    try:

        # Get Main path and test if exists
        root_path = Path(args.directory)
        if not root_path.exists():
            raise ValueError("'%s' is not a valid path." % (args.directory))

        # Recover modules list
        modules_path = []
        if not args.module_list:
            # Recover all submodules, if no module_list is provided
            all_subfolders = [x for x in root_path.iterdir() if x.is_dir()]
        else:
            all_subfolders = [
                root_path / x for x in args.module_list.split(",")
            ]

        # check if each folder is a valid module or not
        for subfolder in all_subfolders:
            if (subfolder / "__openerp__.py").exists() or (
                subfolder / "__manifest__.py"
            ).exists():
                modules_path.append(subfolder)
            else:
                if args.module_list:
                    _logger.warning(
                        "The module %s was not found in the directory %s"
                        % (subfolder.name, args.directory)
                    )
        _logger.debug(
            "The lib will process the following modules %s"
            % (", ".join([x.name for x in modules_path]))
        )

        for module_path in modules_path:
            _migrate_module(args, module_path)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
